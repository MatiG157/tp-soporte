def validate_cost_data(data):
    errors = []
    required_fields = ["id_viaje"]
    
    for field in required_fields:
        if field not in data:
            errors.append(f"El campo '{field}' es obligatorio.")

    # Validar que los costos sean formados y numéricos positivos (como dicta la regla)
    cost_fields = ["costo_alojamiento", "costo_transporte", "costo_actividades", "costo_comidas"]
    for field in cost_fields:
        if field in data:
            try:
                val = float(data[field])
                if val < 0:
                    errors.append(f"El costo en '{field}' no puede ser negativo.")
            except ValueError:
                errors.append(f"El campo '{field}' debe ser un valor numérico válido.")
                
    # Validar presupuesto inicial vs costo si se recibiese por la request 
    # (la regla de negocio controlará después la coherencia reoptimizando)
    
    return errors
