from app.models.enums.MISSION_STATUS import MissionStatus
from app.models.mission_progress_model import MissionProgressModel
from marshmallow import Schema, fields


class MissionProgressReadSchema(Schema):
    class Meta:
        model = MissionProgressModel

    user_id = fields.UUID(required=True)
    mission_id = fields.UUID(required=True)
    status = fields.Enum(MissionStatus, by_value=True, required=True)
    score = fields.Integer(required=True)
    chosenAnswer = fields.String(allow_none=True)