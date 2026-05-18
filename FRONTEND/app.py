from datetime import datetime, date
from datetime import timedelta
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
import requests

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
# Sesion dura para siempre o mucho tiempo
app.permanent_session_lifetime = timedelta(days=365)

# URL base del backend
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')


# ─── Rutas principales ────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Landing page / Home"""
    # Pasamos el user_id para que Jinja sepa si está logueado o no
    return render_template('index.html', user_id=session.get('user_id'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de usuario"""
    if request.method == 'POST':
        datos = {
            'nombre':       request.form.get('nombre'),
            'apellido':     request.form.get('apellido'),
            'email':        request.form.get('email'),
            'contrasena':   request.form.get('contrasena'),
            'nacionalidad': request.form.get('nacionalidad'),
        }
        try:
            resp = requests.post(f'{BACKEND_URL}/usuarios/', json=datos)
            if resp.status_code == 201:
                return redirect(url_for('login'))
            error = resp.json().get('error') or resp.json().get('errores_validacion')
            return render_template('register.html', error=error)
        except requests.exceptions.ConnectionError:
            return render_template('register.html', error='No se pudo conectar con el servidor.')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuario"""
    if request.method == 'POST':
        # Soporte para fetch (JSON) o form subido normal
        data = request.get_json() if request.is_json else request.form
        email = data.get('email')
        contrasena = data.get('contrasena')
        try:
            resp = requests.post(
                f'{BACKEND_URL}/usuarios/login', json={'email': email, 'contrasena': contrasena})
            if resp.status_code == 200:
                user_data = resp.json()
                session.permanent = True  # Hace que la sesion sea permanente
                session['user_email'] = email
                session['user_id'] = user_data.get('id_usuario')
                if request.is_json:
                    return jsonify({"success": True})
                # dashboard or whatever main route
                return redirect(url_for('compare'))
            else:
                error = resp.json().get('error', 'Credenciales inválidas')
                if request.is_json:
                    return jsonify({"error": error}), 401
                return render_template('login.html', error=error)
        except requests.exceptions.ConnectionError:
            if request.is_json:
                return jsonify({"error": 'No se pudo conectar con el servidor.'}), 500
            return render_template('login.html', error='No se pudo conectar con el servidor.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html')


@app.route('/mytrips')
def mytrips():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    viajes = []

    try:
        resp = requests.get(f'{BACKEND_URL}/viajes/usuario/{user_id}')
        if resp.status_code == 200:
            viajes_data = resp.json()
            # Filip status guardado
            viajes_guardados = [
                v for v in viajes_data if v.get('estado') == 'guardado']

            # Sort by created_at descending
            viajes_guardados.sort(key=lambda x: x.get(
                'created_at') or '', reverse=True)

            hoy = date.today()

            for index, v in enumerate(viajes_guardados):
                f_inicio = datetime.fromisoformat(v['fecha_inicio']).date()
                f_fin = datetime.fromisoformat(v['fecha_fin']).date()

                # Default logic
                if f_fin < hoy:
                    v['status_label'] = 'Past Trip'
                    v['status_class'] = 'bg-secondary'
                    v['is_past'] = True
                elif f_inicio > hoy:
                    v['status_label'] = 'Next Trip'
                    v['status_class'] = 'bg-primary'
                    v['is_past'] = False
                else:
                    v['status_label'] = 'Current Trip'
                    v['status_class'] = 'bg-success'
                    v['is_past'] = False

                # El mas nuevo (index == 0) le ponemos 'New Trip' si no es Past Trip (o simplemente sobreecribimos? "al mas nuevo new trip")
                if index == 0 and not v.get('is_past') and v['status_label'] != 'Current Trip':
                    v['status_label'] = 'New Trip'
                    v['status_class'] = 'bg-info text-dark'

                v['fecha_inicio'] = f_inicio.strftime('%d/%m/%Y')
                v['fecha_fin'] = f_fin.strftime('%d/%m/%Y')

            viajes = viajes_guardados

    except requests.exceptions.ConnectionError:
        pass

    return render_template('mytrips.html', viajes=viajes)


@app.route('/compare')
def compare():
    if 'user_id' not in session:
        # Prevent default 1 if not logged in
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    drafts = []
    try:
        resp = requests.get(f'{BACKEND_URL}/viajes/usuario/{user_id}/drafts')
        if resp.status_code == 200:
            drafts = resp.json()
    except requests.exceptions.ConnectionError:
        pass

    if not drafts:
        return redirect(url_for('index'))

    # Organizar drafts por tipo_viaje
    viajes_por_tipo = {
        'Economy': None,
        'Balanced': None,
        'Luxury': None
    }
    for draft in drafts:
        if draft.get('tipo_viaje') in viajes_por_tipo:
            viajes_por_tipo[draft.get('tipo_viaje')] = draft

    return render_template('compare.html', viajes_por_tipo=viajes_por_tipo)


@app.route('/generate_trips', methods=['GET'])
def generate_trips():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    # Obtener parámetros del query
    destino = request.args.get('destino')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    # Crear 3 opciones genéricas
    opciones = [
        {
            "destino": destino or "Destino Desconocido",
            "fecha_inicio": fecha_inicio or "2024-01-01",
            "fecha_fin": fecha_fin or "2024-01-07",
            "tipo": "Economy",
            "costo_total_estimado": 1000.0
        },
        {
            "destino": destino or "Destino Desconocido",
            "fecha_inicio": fecha_inicio or "2024-01-01",
            "fecha_fin": fecha_fin or "2024-01-07",
            "tipo": "Balanced",
            "costo_total_estimado": 2500.0
        },
        {
            "destino": destino or "Destino Desconocido",
            "fecha_inicio": fecha_inicio or "2024-01-01",
            "fecha_fin": fecha_fin or "2024-01-07",
            "tipo": "Luxury",
            "costo_total_estimado": 5000.0
        }
    ]

    datos = {
        "id_usuario": user_id,
        "opciones": opciones
    }

    try:
        requests.post(f'{BACKEND_URL}/viajes/generate', json=datos)
    except requests.exceptions.ConnectionError:
        pass

    return redirect(url_for('compare'))


@app.route('/select_trip/<int:id_viaje>', methods=['POST'])
def select_trip(id_viaje):
    try:
        resp = requests.post(f'{BACKEND_URL}/viajes/{id_viaje}/select')
        if resp.status_code == 200:
            return redirect(url_for('mytrips'))
    except requests.exceptions.ConnectionError:
        pass
    return redirect(url_for('compare'))


@app.route('/itinerary')
def itinerary():
    # if 'user_id' not in session:
    # return redirect(url_for('login'))
    return render_template('itinerary.html')


@app.route('/planificar', methods=['GET', 'POST'])
def planificar():
    """Formulario para planificar un nuevo viaje con IA"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        preferencias = {
            'destino':           request.form.get('destino'),
            'fecha_inicio':      request.form.get('fecha_inicio'),
            'fecha_fin':         request.form.get('fecha_fin'),
            'costo_max':         float(request.form.get('costo_max', 0)),
            'cantidad_personas': int(request.form.get('cantidad_personas', 1)),
            'grupo':             request.form.get('grupo'),
            'clima':             request.form.get('clima'),
            'otros':             request.form.get('otros'),
        }
        try:
            resp = requests.post(
                f'{BACKEND_URL}/api/recommendations/generate',
                json=preferencias
            )
            if resp.status_code == 200:
                recomendaciones = resp.json().get('data', [])
                return render_template('resultados.html',
                                       recomendaciones=recomendaciones,
                                       preferencias=preferencias)
            error = resp.json().get('error', 'Error al generar recomendaciones.')
            return render_template('planificar.html', error=error)
        except requests.exceptions.ConnectionError:
            return render_template('planificar.html',
                                   error='No se pudo conectar con el servidor.')

    # Cargar tipos de alojamiento para el formulario
    tipos_alojamiento = []
    try:
        resp = requests.get(f'{BACKEND_URL}/tipos_alojamiento/')
        if resp.status_code == 200:
            tipos_alojamiento = resp.json()
    except requests.exceptions.ConnectionError:
        pass

    return render_template('planificar.html', tipos_alojamiento=tipos_alojamiento)


@app.route('/viaje/<int:id_viaje>')
def detalle_viaje(id_viaje):
    """Detalle de un viaje: itinerario, costos y actividades"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    viaje, costos, itinerarios = None, None, []
    try:
        r_viaje = requests.get(f'{BACKEND_URL}/viajes/{id_viaje}')
        if r_viaje.status_code == 200:
            viaje = r_viaje.json()

        r_costos = requests.get(f'{BACKEND_URL}/costos/viajes/{id_viaje}')
        if r_costos.status_code == 200:
            costos = r_costos.json()

        r_itin = requests.get(f'{BACKEND_URL}/itinerarios/viaje/{id_viaje}')
        if r_itin.status_code == 200:
            itinerarios = r_itin.json()
    except requests.exceptions.ConnectionError:
        pass

    return render_template('detalle_viaje.html',
                           viaje=viaje,
                           costos=costos,
                           itinerarios=itinerarios)


# ─── Error handlers ───────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=8080)
