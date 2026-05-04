from marshmallow import Schema, fields, validate


class ActivitySchema(Schema):
    id_itinerario = fields.Integer(
        required=True,
        error_messages={"required": "El ID del itinerario es obligatorio."}
    )
    nombre = fields.String(
        required=True,
        validate=validate.Length(min=2, max=120),
        error_messages={"required": "El nombre es obligatorio."}
    )
    descripcion = fields.String()
    precio_estimado = fields.Float()
    categoria = fields.String(validate=validate.Length(max=80))
    horario_sugerido = fields.String(validate=validate.Length(max=30))
    ubicacion = fields.String(validate=validate.Length(max=150))


activity_schema = ActivitySchema()
