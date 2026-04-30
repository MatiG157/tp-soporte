from flask import Blueprint, request, jsonify
from src.services.itinerary_service import (
    crear_itinerario,
    obtener_itinerarios_por_viaje,
    obtener_itinerario_por_id,
    actualizar_itinerario,
    eliminar_itinerario
)

itinerary_bp = Blueprint('itinerary_bp', __name__, url_prefix='/itinerarios')


@itinerary_bp.route('/', methods=['POST'])
def alta_itinerario():
    datos = request.get_json()

    if not datos or not 'id_viaje' in datos:
        return jsonify({"error": "No se enviaron datos suficientes para crear el itinerario"}), 400

    try:
        nuevo_itinerario = crear_itinerario(datos)
        return jsonify({"mensaje": "Itinerario creado con éxito", "id": nuevo_itinerario.id_itinerario}), 201

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@itinerary_bp.route('/viaje/<int:id_viaje>', methods=['GET'])
def get_itinerarios_viaje(id_viaje):
    itinerarios = obtener_itinerarios_por_viaje(id_viaje)
    if not itinerarios:
        return jsonify({"mensaje": "No se encontraron itinerarios para este viaje"}), 404

    resultado = [{
        "id_itinerario": it.id_itinerario,
        "dia": it.dia,
        "resumen": it.resumen
    } for it in itinerarios]

    return jsonify(resultado), 200


@itinerario_bp.route('/<int:id_itinerario>', methods=['GET'])
def get_itinerario(id_itinerario):
    itinerario = obtener_itinerario_por_id(id_itinerario)
    if not itinerario:
        return jsonify({"error": "Itinerario no encontrado"}), 404

    return jsonify({
        "id_itinerario": itinerario.id_itinerario,
        "id_viaje": itinerario.id_viaje,
        "dia": itinerario.dia,
        "resumen": itinerario.resumen
    }), 200


@itinerary_bp.route('/<int:id_itinerario>', methods=['PUT'])
def modificar_itinerario(id_itinerario):
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "No se enviaron datos para actualizar"}), 400

    try:
        itinerario_actualizado = actualizar_itinerario(id_itinerario, datos)

        if not itinerario_actualizado:
            return jsonify({"error": "Itinerario no encontrado"}), 404

        return jsonify(
            {
                "mensaje": f"Itinerario con ID {id_itinerario} actualizado con éxito",
                "id": itinerario_actualizado.id_itinerario
            }
        ), 200

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error interno: {str(e)}"}), 500


@itinerary_bp.route('/<int:id_itinerario>', methods=['DELETE'])
def baja_itinerario(id_itinerario):
    if eliminar_itinerario(id_itinerario):
        return jsonify({"mensaje": "Itinerario eliminado"}), 200
    return jsonify({"error": "Itinerario no encontrado"}), 404
