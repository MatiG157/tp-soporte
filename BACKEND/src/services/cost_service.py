from src.models.init import db
from src.models.cost import Costo

def calculate_base_cost(data):
    """Regla de Negocio de Cálculo: combina el precio de alojamiento, transporte, actividades diarias y comida."""
    c_alojamiento = float(data.get('costo_alojamiento', 0))
    c_transporte = float(data.get('costo_transporte', 0))
    c_actividades = float(data.get('costo_actividades', 0))
    c_comidas = float(data.get('costo_comidas', 0))
    
    return c_alojamiento + c_transporte + c_actividades + c_comidas

def apply_cost_adjustment(base_cost, tipo_viaje):
    """Regla de Negocio: ajusta el valor final según el tipo de viaje elegido."""
    tipo = str(tipo_viaje).lower()
    
    # Supongamos un factor de ajuste según el tipo de viaje
    multiplier = 1.0
    if tipo in ["economico", "mochilero"]:
        multiplier = 0.90 # 10% de ahorro estimado o descuento
    elif tipo in ["lujo", "premium"]:
        multiplier = 1.25 # 25% extra por costos servicios premium
    elif tipo in ["confort"]:
        multiplier = 1.10
        
    return base_cost * multiplier

def create_or_update_cost(data):
    id_viaje = data['id_viaje']
    
    # 1. Aplicar la Regla de Negocio de Cálculo
    total_base = calculate_base_cost(data)
    
    # Buscar si ya existe el costo asociado al viaje
    costo_existente = Costo.query.filter_by(id_viaje=id_viaje).first()
    
    if costo_existente:
        costo_existente.costo_alojamiento = data.get('costo_alojamiento', costo_existente.costo_alojamiento)
        costo_existente.costo_transporte = data.get('costo_transporte', costo_existente.costo_transporte)
        costo_existente.costo_actividades = data.get('costo_actividades', costo_existente.costo_actividades)
        costo_existente.costo_comidas = data.get('costo_comidas', costo_existente.costo_comidas)
        costo_existente.costo_total_base = calculate_base_cost({
            'costo_alojamiento': costo_existente.costo_alojamiento,
            'costo_transporte': costo_existente.costo_transporte,
            'costo_actividades': costo_existente.costo_actividades,
            'costo_comidas': costo_existente.costo_comidas
        })
        costo_obj = costo_existente
    else:
        nuevo_costo = Costo(
            id_viaje=id_viaje,
            costo_alojamiento=data.get('costo_alojamiento', 0),
            costo_transporte=data.get('costo_transporte', 0),
            costo_actividades=data.get('costo_actividades', 0),
            costo_comidas=data.get('costo_comidas', 0),
            costo_total_base=total_base
        )
        db.session.add(nuevo_costo)
        costo_obj = nuevo_costo
        
    db.session.commit()
    
    return {
        "id_costo": costo_obj.id_costo,
        "id_viaje": costo_obj.id_viaje,
        "costo_total_base": costo_obj.costo_total_base
    }

def get_cost_by_trip(id_viaje, tipo_viaje=None):
    costo = Costo.query.filter_by(id_viaje=id_viaje).first()
    if not costo:
        return None
        
    response = {
        "id_costo": costo.id_costo,
        "id_viaje": costo.id_viaje,
        "costo_alojamiento": costo.costo_alojamiento,
        "costo_transporte": costo.costo_transporte,
        "costo_actividades": costo.costo_actividades,
        "costo_comidas": costo.costo_comidas,
        "costo_total_base": costo.costo_total_base
    }
    
    if tipo_viaje:
        costo_final = apply_cost_adjustment(costo.costo_total_base, tipo_viaje)
        response["tipo_viaje_aplicado"] = tipo_viaje
        response["costo_total_ajustado"] = costo_final
        
    return response