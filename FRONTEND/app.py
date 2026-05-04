import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# URL base del backend
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')


# ─── Rutas principales ────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Landing page / Home"""
    return render_template('index.html')


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
    """Login de usuario (simplificado, sin JWT por ahora)"""
    if request.method == 'POST':
        # Placeholder: acá iría la lógica de autenticación real
        # cuando el backend tenga el endpoint /login
        email = request.form.get('email')
        session['user_email'] = email
        session['user_id'] = 1  # temporal hasta tener auth real
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))



@app.route('/mytrips')
def mytrips():
   return render_template('mytrips.html') 

@app.route('/dashboard')
def dashboard():
    """Panel principal del usuario con sus viajes"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    viajes = []
    try:
        resp = requests.get(f'{BACKEND_URL}/viajes/usuario/{session["user_id"]}')
        if resp.status_code == 200:
            viajes = resp.json()
    except requests.exceptions.ConnectionError:
        pass  # El template maneja la lista vacía

    return render_template('dashboard.html', viajes=viajes)


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
