from app.models.missions_model import MissionsModel
from app.models.enums.MISSION_TIER import MissionTier
from app.domain.errors import ValidationError


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

        missing = [
            field for field, value in {
                "mission_name": mission_name,
                "question": question,
                "possible_answers": possible_answers,
                "answer": answer,
                "tier": tier,
            }.items() if not value
        ]

        if missing:
            raise ValidationError(
                message="Missing required fields",
                details={"missing": missing}
            )

        tier_map = {
            "1": MissionTier.EASY,
            "2": MissionTier.MEDIUM,
            "3": MissionTier.HARD,
        }
        
        role_enum = tier_map.get(tier, MissionTier.MEDIUM)
        if role_enum is None:
            raise ValidationError(message="Invalid tier value")

        with self.uow:

            mission = MissionsModel(
                mission_name=mission_name,
                question=question,
                possible_answers=possible_answers,
                answer=answer,
                tier=role_enum
            )

            self.missions_repo.add(mission)

            self.uow.commit()
        return mission