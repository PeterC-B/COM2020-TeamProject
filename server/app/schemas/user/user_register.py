from marshmallow import Schema, fields, validate


class UserRegisterSchema(Schema):
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=50))

    password = fields.String(required=True, validate=validate.Length(min=6))