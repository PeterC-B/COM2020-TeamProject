from marshmallow import Schema, fields
from sqlalchemy import UUID
from sqlalchemy import Enum
from app.models.enums.ACCESS_TYPE import UserAccessType

class UserReadSchema(Schema):
    user_id = fields.UUID(required=True)
    username = fields.String(required=True)
    role = fields.Enum(UserAccessType, by_value=True, required=True)
    created_at = fields.DateTime(required=True)