from app.extensions import ma
from app.models.missions_model import MissionsModel


class MissionReadSchema(ma.SQLAlchemySchema):
    class Meta:
        model = MissionsModel

    mission_id = ma.auto_field()
    mission_name = ma.auto_field()
    question = ma.auto_field()
    possible_answers = ma.auto_field()
    answer = ma.auto_field()
    tier = ma.auto_field()
