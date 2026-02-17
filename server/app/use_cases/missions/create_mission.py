from server.app.models.missions_model import MissionsModel
from server.app.models.enums.MISSION_TIER import MissionTier
from server.app.domain.errors import ValidationError


class CreateMission:
    def __init__(self, uow, missions_repo):
        self.uow = uow
        self.missions_repo = missions_repo


    def execute(self, payload):
        mission_name = payload.get('mission_name')
        question = payload.get('question')
        possible_answers = payload.get('possible_answers')
        answer = payload.get('answer')
        tier = payload.get('tier')

        tier_map = {
            "1": MissionTier.EASY,
            "2": MissionTier.MEDIUM,
            "3": MissionTier.HARD,
        }
        role_enum = tier_map.get(tier or 1)
        if role_enum is None:
            raise ValidationError(message="Invalid role value")

        with self.uow:

            mission = MissionsModel(
                mission_name=mission_name,
                question=question,
                possible_answers=possible_answers,
                answer=answer,
                tier=role_enum
            )

            self.missions_repo.add(mission_name)

            self.uow.commit()
        return MissionsModel(mission_id=str(mission.mission_id))