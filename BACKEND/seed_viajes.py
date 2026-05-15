import uuid
from datetime import datetime, timedelta, timezone
from app import app
from src.models.init import db
from src.models.trip import Viaje

with app.app_context():
    ahora = datetime.now(timezone.utc).date()

    # Usuarios para los que queremos sembrar viajes
    usuarios_ids = [1, 2]

    viajes_a_crear = []

    for uid in usuarios_ids:
        # 1. Crear 3 viajes en DRAFT con el mismo group_id para el usuario
        draft_group_id = str(uuid.uuid4())

        viaje_draft_1 = Viaje(
            id_usuario=uid, destino="Tokio - Economy",
            fecha_inicio=ahora, fecha_fin=ahora + timedelta(days=7),
            tipo_viaje="Economy", costo_total_estimado=1250.0, estado="draft", group_id=draft_group_id,
            imagen="https://images.unsplash.com/photo-1540959733332-eab4deabeeaf"
        )
        viaje_draft_2 = Viaje(
            id_usuario=uid, destino="Tokio - Balanced",
            fecha_inicio=ahora, fecha_fin=ahora + timedelta(days=7),
            tipo_viaje="Balanced", costo_total_estimado=2850.0, estado="draft", group_id=draft_group_id,
            imagen="https://images.unsplash.com/photo-1499856871958-5b9627545d1a"
        )
        viaje_draft_3 = Viaje(
            id_usuario=uid, destino="Tokio - Luxury",
            fecha_inicio=ahora, fecha_fin=ahora + timedelta(days=7),
            tipo_viaje="Luxury", costo_total_estimado=5200.0, estado="draft", group_id=draft_group_id,
            imagen="https://images.unsplash.com/photo-1563911302283-d2bc129e7570"
        )

        # 2. Crear 2 viajes GUARDADOS con distinto group_id para cada uno
        viaje_guardado_1 = Viaje(
            id_usuario=uid, destino=f"París - Viaje de Usuario {uid}",
            fecha_inicio=ahora, fecha_fin=ahora + timedelta(days=5),
            tipo_viaje="Balanced", costo_total_estimado=3000.0, estado="guardado", group_id=str(uuid.uuid4()),
            imagen="https://images.unsplash.com/photo-1502602898657-3e91760cbb34"
        )
        viaje_guardado_2 = Viaje(
            id_usuario=uid, destino=f"Roma - Viaje de Usuario {uid}",
            fecha_inicio=ahora, fecha_fin=ahora + timedelta(days=4),
            tipo_viaje="Luxury", costo_total_estimado=4500.0, estado="guardado", group_id=str(uuid.uuid4()),
            imagen="https://images.unsplash.com/photo-1552832230-c0197dd311b5"
        )

        # Agregamos todos los viajes generados para este usuario a la lista general
        viajes_a_crear.extend(
            [viaje_draft_1, viaje_draft_2, viaje_draft_3, viaje_guardado_1, viaje_guardado_2])

    # Insertamos y guardamos todos los viajes de una vez
    db.session.add_all(viajes_a_crear)
    db.session.commit()

    print("¡Base de datos sembrada correctamente con viajes para los usuarios 1 y 2!")
