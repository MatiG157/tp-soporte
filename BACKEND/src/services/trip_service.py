from src.models.init import db
from src.models.trip import Viaje
from src.models.user import Usuario
from src.validators.trip_validator import viaje_schema


def crear_viaje(datos):
    # Deserializa y valida con Marshmallow
    datos_validados = viaje_schema.load(datos)

    # Validamos que el usuario "dueño" del viaje exista en la DB
    usuario = Usuario.query.get(datos_validados['id_usuario'])
    if not usuario:
        raise ValueError(
            f"No se encontró un usuario con ID {datos_validados['id_usuario']}")

    nuevo_viaje = Viaje(
        id_usuario=datos_validados['id_usuario'],
        destino=datos_validados['destino'],
        fecha_inicio=datos_validados['fecha_inicio'],
        fecha_fin=datos_validados['fecha_fin'],
        tipo_viaje=datos_validados['tipo_viaje'],
        costo_total_estimado=datos_validados.get('costo_total_estimado')
    )

    db.session.add(nuevo_viaje)
    db.session.commit()
    return nuevo_viaje


def obtener_viajes_por_usuario(id_usuario):
    return Viaje.query.filter_by(id_usuario=id_usuario).all()


def obtener_viaje_por_id(id_viaje):
    return Viaje.query.get(id_viaje)


def actualizar_viaje(id_viaje, datos):
    datos_validados = viaje_schema.load(datos, partial=True)
    viaje = Viaje.query.get(id_viaje)

    if not viaje:
        return None

    viaje.destino = datos_validados.get('destino', viaje.destino)
    viaje.fecha_inicio = datos_validados.get(
        'fecha_inicio', viaje.fecha_inicio)
    viaje.fecha_fin = datos_validados.get('fecha_fin', viaje.fecha_fin)
    viaje.tipo_viaje = datos_validados.get('tipo_viaje', viaje.tipo_viaje)
    viaje.costo_total_estimado = datos_validados.get(
        'costo_total_estimado', viaje.costo_total_estimado)

    db.session.commit()
    return viaje


def eliminar_viaje(id_viaje):
    viaje = Viaje.query.get(id_viaje)
    if viaje:
        db.session.delete(viaje)
        db.session.commit()
        return True
    return False
