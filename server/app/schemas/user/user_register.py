from marshmallow import Schema, fields, validate


class UserRegisterSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=1, max=50))

    email = fields.Email(required=True, validate=validate.Length(max=50))

    password = fields.String(required=True, validate=validate.Length(min=6))

    role = fields.String(
        required=False,
        validate=validate.OneOf(
            ["travellers", "administrators", "developers"],
        ),
    )
