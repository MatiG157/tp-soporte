from marshmallow import Schema, fields, validate


class AccommodationTypeSchema(Schema):
    tipo = fields.String(
        required=True,
        validate=validate.Length(min=2, max=50),
        error_messages={"required": "El tipo de alojamiento es obligatorio."}
    )


accommodation_type_schema = AccommodationTypeSchema()
