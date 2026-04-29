from flask import Blueprint, request, jsonify
from src.services.cost_service import create_or_update_cost, get_cost_by_trip
from src.validators.cost_validator import validate_cost_data

cost_bp = Blueprint('cost_bp', __name__)

@cost_bp.route('/', methods=['POST', 'PUT'])
def save_cost_route():
    data = request.json
    errors = validate_cost_data(data)
    
    if errors:
        return jsonify({"errores": errors}), 400

    try:
        resultado = create_or_update_cost(data)
        return jsonify({
            "mensaje": "Costo guardado exitosamente aplicando reglas de cálculo",
            "datos": resultado
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cost_bp.route('/viajes/<int:id_viaje>', methods=['GET'])
def get_cost_route(id_viaje):
    # El Frontend puede enviar el parámetro tipo_viaje para aplicar el ajuste
    tipo_viaje = request.args.get('tipo_viaje')
    
    try:
        resultado = get_cost_by_trip(id_viaje, tipo_viaje)
        if not resultado:
            return jsonify({"error": "Costos no encontrados para el viaje especificado"}), 404
            
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
