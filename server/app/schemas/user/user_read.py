from marshmallow import Schema, fields


class UserReadSchema(Schema):
    id = fields.Int(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    created_at = fields.DateTime(required=True)