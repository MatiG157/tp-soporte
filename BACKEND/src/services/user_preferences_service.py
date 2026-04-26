from src.models.init import db
from src.models.user_preferences import PreferenciasUsuario
from validators.user_preferences_validator import user_preferences_schema

def crear_preferencia(datos):
    datos_validados = user_preferences_schema.load(datos)
    
    nueva_preferencia = PreferenciasUsuario(
        id_usuario=datos_validados['id_usuario'],
        destino=datos_validados.get('destino'),
        costo_min=datos_validados.get('costo_min'),
        costo_max=datos_validados.get('costo_max'),
        cantidad_personas=datos_validados.get('cantidad_personas'),
        grupo=datos_validados.get('grupo'),
        clima=datos_validados.get('clima'),
        otros=datos_validados.get('otros')
    )
    db.session.add(nueva_preferencia)
    db.session.commit()
    return nueva_preferencia

def eliminar_preferencia(id_preferencia):
    preferencia = PreferenciasUsuario.query.get(id_preferencia)
    if preferencia:
        db.session.delete(preferencia)
        db.session.commit()
        return True
    return False

def actualizar_preferencia(id_preferencia, datos):
    # partial=True para soportar actualizaciones parciales en PUT/PATCH
    datos_validados = user_preferences_schema.load(datos, partial=True)
    preferencia = PreferenciasUsuario.query.get(id_preferencia)
    
    if not preferencia:
        return None 
        
    preferencia.destino = datos_validados.get('destino', preferencia.destino)
    preferencia.costo_min = datos_validados.get('costo_min', preferencia.costo_min)
    preferencia.costo_max = datos_validados.get('costo_max', preferencia.costo_max)
    preferencia.cantidad_personas = datos_validados.get('cantidad_personas', preferencia.cantidad_personas)
    preferencia.grupo = datos_validados.get('grupo', preferencia.grupo)
    preferencia.clima = datos_validados.get('clima', preferencia.clima)
    preferencia.otros = datos_validados.get('otros', preferencia.otros)
    
    db.session.commit()
    return preferencia