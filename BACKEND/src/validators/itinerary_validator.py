from marshmallow import Schema, fields, validate


class ItinerarioSchema(Schema):
    id_viaje = fields.Integer(
        required=True,
        error_messages={"required": "El ID del viaje es obligatorio."}
    )
    dia = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        error_messages={"required": "El día es obligatorio."}
    )
    resumen = fields.String()


itinerario_schema = ItinerarioSchema()
itinerarios_schema = ItinerarioSchema(many=True)
