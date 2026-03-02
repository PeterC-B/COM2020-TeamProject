from server.app.models.enums.MISSION_TIER import MissionTier
from server.app.models.mission_progress_model import MissionProgressModel
from marshmallow import Schema, fields


class MissionProgressReadSchema(Schema):
    class Meta:
        model = MissionProgressModel

    user_id = fields.UUID(required=True)
    mission_id = fields.UUID(required=True)
    status = fields.String(required=True) 
    score = fields.Integer(required=True)
    
