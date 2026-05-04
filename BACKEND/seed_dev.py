import argparse
import os
from datetime import date

from flask import Flask
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

from src.models.init import db
from src.models.user import Usuario
from src.models.user_preferences import PreferenciasUsuario
from src.models.accommodation_type import TipoAlojamiento
from src.models.trip import Viaje
from src.models.cost import Costo
from src.models.itinerary import Itinerario
from src.models.activity import Actividad
from src.models.ai_recommendation import RecomendacionIA


load_dotenv()


def create_seed_app():
    app = Flask(__name__)

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    return app


def get_or_create(model, defaults=None, **filters):
    instance = model.query.filter_by(**filters).one_or_none()
    if instance is not None:
        return instance, False

    params = dict(filters)
    if defaults:
        params.update(defaults)

    instance = model(**params)
    db.session.add(instance)
    db.session.flush()
    return instance, True


def seed_accommodation_types():
    types = ["Hotel", "Hostal", "Airbnb", "Resort", "Apartamento"]
    created = []

    for accommodation_type in types:
        instance, was_created = get_or_create(TipoAlojamiento, tipo=accommodation_type)
        if was_created:
            created.append(instance.tipo)

    return created


def seed_users():
    sample_users = [
        {
            "nombre": "Ana",
            "apellido": "Gomez",
            "email": "ana.gomez.dev@example.com",
            "contrasena": "DevPass123",
            "nacionalidad": "Argentina",
        },
        {
            "nombre": "Lucas",
            "apellido": "Perez",
            "email": "lucas.perez.dev@example.com",
            "contrasena": "DevPass123",
            "nacionalidad": "Chile",
        },
        {
            "nombre": "Marta",
            "apellido": "Lopez",
            "email": "marta.lopez.dev@example.com",
            "contrasena": "DevPass123",
            "nacionalidad": "España",
        },
    ]

    users = []
    for user_data in sample_users:
        user = Usuario.query.filter_by(email=user_data["email"]).one_or_none()
        if user is None:
            user = Usuario(
                nombre=user_data["nombre"],
                apellido=user_data["apellido"],
                email=user_data["email"],
                contrasena=generate_password_hash(user_data["contrasena"]),
                nacionalidad=user_data["nacionalidad"],
            )
            db.session.add(user)
            db.session.flush()
        users.append(user)

    return users


def seed_preferences(users):
    accommodation_types = {item.tipo: item for item in TipoAlojamiento.query.all()}

    preference_specs = [
        {
            "user_email": "ana.gomez.dev@example.com",
            "destino": "Lisboa",
            "costo_min": 900,
            "costo_max": 1800,
            "cantidad_personas": 2,
            "grupo": "pareja",
            "clima": "templado",
            "edades_viajeros": "29, 31",
            "tipo_transporte": "Plane",
            "fecha_inicio": date(2026, 7, 10),
            "fecha_fin": date(2026, 7, 16),
            "otros": "Prefiere hotel céntrico y caminatas gastronómicas.",
            "tipos_alojamiento": ["Hotel", "Apartamento"],
        },
        {
            "user_email": "lucas.perez.dev@example.com",
            "destino": "Bariloche",
            "costo_min": 600,
            "costo_max": 1400,
            "cantidad_personas": 4,
            "grupo": "amigos",
            "clima": "frío",
            "edades_viajeros": "27, 28, 29, 30",
            "tipo_transporte": "Car",
            "fecha_inicio": date(2026, 8, 2),
            "fecha_fin": date(2026, 8, 8),
            "otros": "Quiere actividades de montaña y alojamiento con buena vista.",
            "tipos_alojamiento": ["Hostal", "Airbnb"],
        },
        {
            "user_email": "marta.lopez.dev@example.com",
            "destino": "Tokio",
            "costo_min": 2200,
            "costo_max": 4200,
            "cantidad_personas": 1,
            "grupo": "solo",
            "clima": "variable",
            "edades_viajeros": "34",
            "tipo_transporte": "Plane",
            "fecha_inicio": date(2026, 9, 12),
            "fecha_fin": date(2026, 9, 24),
            "otros": "Interés en cultura, tecnología y comida local.",
            "tipos_alojamiento": ["Hotel", "Resort"],
        },
    ]

    preferences = []
    user_by_email = {user.email: user for user in users}

    for spec in preference_specs:
        existing = PreferenciasUsuario.query.filter_by(
            id_usuario=user_by_email[spec["user_email"]].id_usuario,
            destino=spec["destino"],
            fecha_inicio=spec["fecha_inicio"],
            fecha_fin=spec["fecha_fin"],
        ).one_or_none()

        if existing is None:
            existing = PreferenciasUsuario(
                id_usuario=user_by_email[spec["user_email"]].id_usuario,
                destino=spec["destino"],
                costo_min=spec["costo_min"],
                costo_max=spec["costo_max"],
                cantidad_personas=spec["cantidad_personas"],
                grupo=spec["grupo"],
                clima=spec["clima"],
                edades_viajeros=spec["edades_viajeros"],
                tipo_transporte=spec["tipo_transporte"],
                fecha_inicio=spec["fecha_inicio"],
                fecha_fin=spec["fecha_fin"],
                otros=spec["otros"],
            )
            for accommodation_type in spec["tipos_alojamiento"]:
                existing.tipos_alojamiento.append(accommodation_types[accommodation_type])
            db.session.add(existing)
            db.session.flush()

        preferences.append(existing)

    return preferences


def seed_trips(users):
    trip_specs = [
        {
            "user_email": "ana.gomez.dev@example.com",
            "destino": "Lisboa",
            "fecha_inicio": date(2026, 7, 10),
            "fecha_fin": date(2026, 7, 16),
            "tipo_viaje": "pareja",
            "costo_total_estimado": 1650.0,
        },
        {
            "user_email": "lucas.perez.dev@example.com",
            "destino": "Bariloche",
            "fecha_inicio": date(2026, 8, 2),
            "fecha_fin": date(2026, 8, 8),
            "tipo_viaje": "amigos",
            "costo_total_estimado": 1280.0,
        },
        {
            "user_email": "marta.lopez.dev@example.com",
            "destino": "Tokio",
            "fecha_inicio": date(2026, 9, 12),
            "fecha_fin": date(2026, 9, 24),
            "tipo_viaje": "solo",
            "costo_total_estimado": 3550.0,
        },
    ]

    trips = []
    user_by_email = {user.email: user for user in users}

    for spec in trip_specs:
        trip = Viaje.query.filter_by(
            id_usuario=user_by_email[spec["user_email"]].id_usuario,
            destino=spec["destino"],
            fecha_inicio=spec["fecha_inicio"],
            fecha_fin=spec["fecha_fin"],
        ).one_or_none()

        if trip is None:
            trip = Viaje(
                id_usuario=user_by_email[spec["user_email"]].id_usuario,
                destino=spec["destino"],
                fecha_inicio=spec["fecha_inicio"],
                fecha_fin=spec["fecha_fin"],
                tipo_viaje=spec["tipo_viaje"],
                costo_total_estimado=spec["costo_total_estimado"],
            )
            db.session.add(trip)
            db.session.flush()

        trips.append(trip)

    return trips


def seed_trip_details(trips):
    detail_specs = [
        {
            "destino": "Lisboa",
            "costo": {
                "costo_alojamiento": 720,
                "costo_transporte": 380,
                "costo_actividades": 260,
                "costo_comidas": 290,
                "costo_total_base": 1650,
            },
            "itinerarios": [
                {
                    "dia": 1,
                    "resumen": "Llegada, check-in y paseo por Alfama al atardecer.",
                    "actividades": [
                        ("Traslado al hotel", "Check-in y descanso breve", 0, "Logística", "15:00", "Centro de Lisboa"),
                        ("Cena en mirador", "Cena con vista al río Tajo", 90, "Gastronomía", "20:00", "Alfama"),
                    ],
                },
                {
                    "dia": 2,
                    "resumen": "Centro histórico, tranvía y comida local.",
                    "actividades": [
                        ("Tour a pie", "Recorrido guiado por Baixa y Chiado", 45, "Cultural", "10:00", "Baixa"),
                        ("Tranvía 28", "Paseo clásico por la ciudad", 18, "Turismo", "16:00", "Lisboa"),
                    ],
                },
            ],
            "recomendacion": "Conviene reservar alojamiento central y dejar una tarde libre para escapadas gastronómicas.",
        },
        {
            "destino": "Bariloche",
            "costo": {
                "costo_alojamiento": 420,
                "costo_transporte": 260,
                "costo_actividades": 360,
                "costo_comidas": 240,
                "costo_total_base": 1280,
            },
            "itinerarios": [
                {
                    "dia": 1,
                    "resumen": "Llegada, compras y paseo por el centro cívico.",
                    "actividades": [
                        ("Centro cívico", "Fotos y caminata suave", 0, "Cultural", "11:00", "Centro de Bariloche"),
                        ("Cervecería artesanal", "Cena con degustación", 55, "Gastronomía", "21:00", "Bariloche"),
                    ],
                },
                {
                    "dia": 2,
                    "resumen": "Circuito Chico y miradores.",
                    "actividades": [
                        ("Circuito Chico", "Ruta panorámica en auto", 60, "Paisaje", "09:30", "Lago Nahuel Huapi"),
                        ("Cerro Campanario", "Subida en aerosilla", 35, "Aventura", "14:00", "Campanario"),
                    ],
                },
            ],
            "recomendacion": "Para este viaje conviene combinar hostal o Airbnb con excursiones en grupo para optimizar costos.",
        },
        {
            "destino": "Tokio",
            "costo": {
                "costo_alojamiento": 1650,
                "costo_transporte": 820,
                "costo_actividades": 610,
                "costo_comidas": 470,
                "costo_total_base": 3550,
            },
            "itinerarios": [
                {
                    "dia": 1,
                    "resumen": "Llegada, adaptación horaria y paseo nocturno por Shinjuku.",
                    "actividades": [
                        ("Check-in y descanso", "Recuperación del vuelo largo", 0, "Logística", "15:00", "Shinjuku"),
                        ("Observatorio", "Vistas nocturnas de la ciudad", 20, "Turismo", "20:30", "Shinjuku"),
                    ],
                },
                {
                    "dia": 2,
                    "resumen": "Templo, mercado y tecnología.",
                    "actividades": [
                        ("Templo Senso-ji", "Visita cultural temprana", 0, "Cultural", "09:00", "Asakusa"),
                        ("Akihabara", "Recorrido por tiendas y arcades", 25, "Tecnología", "16:00", "Akihabara"),
                    ],
                },
            ],
            "recomendacion": "Usar transporte público y reservar hotel con buena conexión al metro mejora mucho la experiencia.",
        },
    ]

    trips_by_destination = {trip.destino: trip for trip in trips}

    for spec in detail_specs:
        trip = trips_by_destination[spec["destino"]]

        cost = Costo.query.filter_by(id_viaje=trip.id_viaje).one_or_none()
        if cost is None:
            cost = Costo(id_viaje=trip.id_viaje, **spec["costo"])
            db.session.add(cost)

        recommendation = RecomendacionIA.query.filter_by(
            id_viaje=trip.id_viaje,
            tipo="itinerario",
        ).one_or_none()
        if recommendation is None:
            recommendation = RecomendacionIA(
                id_viaje=trip.id_viaje,
                texto_generado=spec["recomendacion"],
                tipo="itinerario",
            )
            db.session.add(recommendation)

        for itinerary_spec in spec["itinerarios"]:
            itinerary = Itinerario.query.filter_by(
                id_viaje=trip.id_viaje,
                dia=itinerary_spec["dia"],
            ).one_or_none()

            if itinerary is None:
                itinerary = Itinerario(
                    id_viaje=trip.id_viaje,
                    dia=itinerary_spec["dia"],
                    resumen=itinerary_spec["resumen"],
                )
                db.session.add(itinerary)
                db.session.flush()

            for activity_data in itinerary_spec["actividades"]:
                nombre, descripcion, precio_estimado, categoria, horario_sugerido, ubicacion = activity_data
                activity = Actividad.query.filter_by(
                    id_itinerario=itinerary.id_itinerario,
                    nombre=nombre,
                ).one_or_none()

                if activity is None:
                    activity = Actividad(
                        id_itinerario=itinerary.id_itinerario,
                        nombre=nombre,
                        descripcion=descripcion,
                        precio_estimado=precio_estimado,
                        categoria=categoria,
                        horario_sugerido=horario_sugerido,
                        ubicacion=ubicacion,
                    )
                    db.session.add(activity)


def clear_sample_data():
    db.session.query(Actividad).delete(synchronize_session=False)
    db.session.query(Itinerario).delete(synchronize_session=False)
    db.session.query(RecomendacionIA).delete(synchronize_session=False)
    db.session.query(Costo).delete(synchronize_session=False)
    db.session.query(Viaje).delete(synchronize_session=False)
    db.session.query(PreferenciasUsuario).delete(synchronize_session=False)
    db.session.query(TipoAlojamiento).delete(synchronize_session=False)
    db.session.query(Usuario).delete(synchronize_session=False)
    db.session.commit()


def run_seed(reset=False):
    if reset:
        clear_sample_data()

    seed_accommodation_types()
    users = seed_users()
    seed_preferences(users)
    trips = seed_trips(users)
    seed_trip_details(trips)
    db.session.commit()


def main():
    parser = argparse.ArgumentParser(description="Seed de desarrollo para la base de datos.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Elimina los datos existentes antes de cargar los datos de prueba.",
    )
    args = parser.parse_args()

    app = create_seed_app()

    with app.app_context():
        db.create_all()
        run_seed(reset=args.reset)
        print("Seed de desarrollo completado.")


if __name__ == "__main__":
    main()