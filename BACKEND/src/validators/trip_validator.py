from marshmallow import Schema, fields, validate


class ViajeSchema(Schema):
    id_usuario = fields.Integer(
        required=True,
        error_messages={"required": "El ID del usuario es obligatorio."}
    )
    destino = fields.String(
        required=True,
        validate=validate.Length(min=2, max=120),
        error_messages={"required": "El destino es obligatorio."}
    )
    fecha_inicio = fields.Date(
        required=True,
        error_messages={
            "required": "La fecha de inicio es obligatoria.",
            "invalid": "Formato inválido. Usa YYYY-MM-DD."
        }
    )
    fecha_fin = fields.Date(
        required=True,
        error_messages={
            "required": "La fecha de fin es obligatoria.",
            "invalid": "Formato inválido. Usa YYYY-MM-DD."
        }
    )
    tipo_viaje = fields.String(
        required=True,
        validate=validate.Length(max=20),
        error_messages={"required": "El tipo de viaje es obligatorio."}
    )
    costo_total_estimado = fields.Float()


viaje_schema = ViajeSchema()
