from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from src.services.accommodatio_service import (
    crear_tipo_alojamiento,
    obtener_tipos_alojamiento,
    obtener_tipo_alojamiento_por_id,
    actualizar_tipo_alojamiento,
    eliminar_tipo_alojamiento
)

accommodation_types_bp = Blueprint('accommodation_types_bp', __name__, url_prefix='/tipos_alojamiento')


@accommodation_types_bp.route('/', methods=['POST'])
def alta_tipo_alojamiento():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos para crear el tipo de alojamiento"}), 400

    try:
        nuevo_tipo = crear_tipo_alojamiento(datos)
        return jsonify({"mensaje": "Tipo de alojamiento creado", "id": nuevo_tipo.id_tipo}), 201
    except ValidationError as err:
        return jsonify({"errores_validacion": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@accommodation_types_bp.route('/', methods=['GET'])
def get_tipos_alojamiento():
    tipos = obtener_tipos_alojamiento()
    if not tipos:
        return jsonify({"mensaje": "No hay tipos de alojamiento"}), 404

    resultado = [{"id_tipo": t.id_tipo, "tipo": t.tipo} for t in tipos]
    return jsonify(resultado), 200


@accommodation_types_bp.route('/<int:id_tipo>', methods=['GET'])
def get_tipo_alojamiento(id_tipo):
    tipo = obtener_tipo_alojamiento_por_id(id_tipo)
    if not tipo:
        return jsonify({"error": "Tipo de alojamiento no encontrado"}), 404

    return jsonify({"id_tipo": tipo.id_tipo, "tipo": tipo.tipo}), 200


@accommodation_types_bp.route('/<int:id_tipo>', methods=['PUT', 'PATCH'])
def modificar_tipo_alojamiento(id_tipo):
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos"}), 400

    try:
        tipo_actualizado = actualizar_tipo_alojamiento(id_tipo, datos)
        if not tipo_actualizado:
            return jsonify({"error": "Tipo de alojamiento no encontrado"}), 404

        return jsonify({"mensaje": "Tipo de alojamiento actualizado", "id": tipo_actualizado.id_tipo}), 200
    except ValidationError as err:
        return jsonify({"errores_validacion": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@accommodation_types_bp.route('/<int:id_tipo>', methods=['DELETE'])
def baja_tipo_alojamiento(id_tipo):
    if eliminar_tipo_alojamiento(id_tipo):
        return jsonify({"mensaje": "Tipo de alojamiento eliminado"}), 200
    return jsonify({"error": "Tipo de alojamiento no encontrado"}), 404
