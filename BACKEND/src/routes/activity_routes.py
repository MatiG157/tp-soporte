from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from src.services.activity_service import (
    crear_actividad,
    obtener_actividades_por_itinerario,
    obtener_actividad_por_id,
    actualizar_actividad,
    eliminar_actividad
)

activity_bp = Blueprint('activity_bp', __name__, url_prefix='/actividades')


@activity_bp.route('/', methods=['POST'])
def alta_actividad():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos para crear la actividad"}), 400

    try:
        nueva_actividad = crear_actividad(datos)
        return jsonify({"mensaje": "Actividad creada", "id": nueva_actividad.id_actividad}), 201
    except ValidationError as err:
        return jsonify({"errores_validacion": err.messages}), 400
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activity_bp.route('/itinerario/<int:id_itinerario>', methods=['GET'])
def get_actividades_itinerario(id_itinerario):
    actividades = obtener_actividades_por_itinerario(id_itinerario)
    if not actividades:
        return jsonify({"mensaje": "No hay actividades para este itinerario"}), 404

    resultado = [{
        "id_actividad": a.id_actividad,
        "nombre": a.nombre,
        "descripcion": a.descripcion,
        "precio_estimado": a.precio_estimado,
        "categoria": a.categoria,
        "horario_sugerido": a.horario_sugerido,
        "ubicacion": a.ubicacion
    } for a in actividades]

    return jsonify(resultado), 200


@activity_bp.route('/<int:id_actividad>', methods=['GET'])
def get_actividad(id_actividad):
    a = obtener_actividad_por_id(id_actividad)
    if not a:
        return jsonify({"error": "Actividad no encontrada"}), 404

    return jsonify({
        "id_actividad": a.id_actividad,
        "id_itinerario": a.id_itinerario,
        "nombre": a.nombre,
        "descripcion": a.descripcion,
        "precio_estimado": a.precio_estimado,
        "categoria": a.categoria,
        "horario_sugerido": a.horario_sugerido,
        "ubicacion": a.ubicacion
    }), 200


@activity_bp.route('/<int:id_actividad>', methods=['PUT', 'PATCH'])
def modificar_actividad(id_actividad):
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos"}), 400

    try:
        actividad_actualizada = actualizar_actividad(id_actividad, datos)
        if not actividad_actualizada:
            return jsonify({"error": "Actividad no encontrada"}), 404

        return jsonify({"mensaje": "Actividad actualizada", "id": actividad_actualizada.id_actividad}), 200

    except ValidationError as err:
        return jsonify({"errores_validacion": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activity_bp.route('/<int:id_actividad>', methods=['DELETE'])
def baja_actividad(id_actividad):
    if eliminar_actividad(id_actividad):
        return jsonify({"mensaje": "Actividad eliminada"}), 200
    return jsonify({"error": "Actividad no encontrada"}), 404
