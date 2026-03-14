from app.models.enums.MISSION_TIER import MissionTier
from app.models.missions_model import MissionsModel
from marshmallow import Schema, fields


class MissionReadSchema(Schema):
    class Meta:
        model = MissionsModel

    mission_id = fields.UUID(required=True)
    mission_name = fields.String(required=True)
    question = fields.String(required=True)
    possible_answers = fields.String(required=True)
    answer = fields.String(required=True)
    tier = fields.Enum(MissionTier, required=True)
