from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from src.services.trip_service import (
    crear_viaje,
    obtener_viajes_por_usuario,
    obtener_viaje_por_id,
    actualizar_viaje,
    eliminar_viaje
)

trip_bp = Blueprint('trip_bp', __name__, url_prefix='/viajes')


@trip_bp.route('/', methods=['POST'])
def alta_viaje():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos para crear el viaje"}), 400

    try:
        nuevo_viaje = crear_viaje(datos)
        return jsonify({"mensaje": "Viaje creado", "id": nuevo_viaje.id_viaje}), 201
    except ValidationError as err:
        return jsonify({"errores_validacion": err.messages}), 400
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trip_bp.route('/usuario/<int:id_usuario>', methods=['GET'])
def get_viajes_usuario(id_usuario):
    viajes = obtener_viajes_por_usuario(id_usuario)
    if not viajes:
        return jsonify({"mensaje": "No hay viajes para este usuario"}), 404

    resultado = [{
        "id_viaje": v.id_viaje,
        "destino": v.destino,
        "fecha_inicio": v.fecha_inicio.isoformat(),
        "fecha_fin": v.fecha_fin.isoformat(),
        "tipo_viaje": v.tipo_viaje,
        "costo_total_estimado": v.costo_total_estimado
    } for v in viajes]

    return jsonify(resultado), 200


@trip_bp.route('/<int:id_viaje>', methods=['GET'])
def get_viaje(id_viaje):
    v = obtener_viaje_por_id(id_viaje)
    if not v:
        return jsonify({"error": "Viaje no encontrado"}), 404

    return jsonify({
        "id_viaje": v.id_viaje,
        "id_usuario": v.id_usuario,
        "destino": v.destino,
        "fecha_inicio": v.fecha_inicio.isoformat(),
        "fecha_fin": v.fecha_fin.isoformat(),
        "tipo_viaje": v.tipo_viaje,
        "costo_total_estimado": v.costo_total_estimado
    }), 200


@trip_bp.route('/<int:id_viaje>', methods=['PUT', 'PATCH'])
def modificar_viaje(id_viaje):
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos"}), 400

    try:
        viaje_actualizado = actualizar_viaje(id_viaje, datos)
        if not viaje_actualizado:
            return jsonify({"error": "Viaje no encontrado"}), 404

        return jsonify({"mensaje": "Viaje actualizado", "id": viaje_actualizado.id_viaje}), 200

    except ValidationError as err:
        return jsonify({"errores_validacion": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trip_bp.route('/<int:id_viaje>', methods=['DELETE'])
def baja_viaje(id_viaje):
    if eliminar_viaje(id_viaje):
        return jsonify({"mensaje": "Viaje eliminado"}), 200
    return jsonify({"error": "Viaje no encontrado"}), 404
