from server.app.models.missions_model import MissionsModel
from server.app.models.enums.MISSION_TIER import MissionTier
from server.app.models.enums.MISSION_STATUS import MissionStatus
from server.app.models.mission_progress_model import MissionProgressModel
from server.app.domain.errors import ValidationError


class SaveMissionProgress:
    def __init__(self, uow, missions_repo):
        self.uow = uow
        self.missions_repo = missions_repo


    def execute(self, payload):
        user_id = payload.get('user_id')
        mission_id = payload.get('mission_id')
        status = payload.get('status')
        tier = payload.get('tier')

        missing = [
            field for field, value in {
                "username": user_id,
                "mission": mission_id,
                "status": status,
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

        score_map = {
            "1": 10,
            "2": 20,
            "3": 30,
        }
        
        role_enum = tier_map.get(tier, MissionTier.MEDIUM)
        score_value = score_map.get(tier, 0)
        if role_enum is None:
            raise ValidationError(message="Invalid tier value")

        with self.uow:

            progress = MissionProgressModel(
                user_id=user_id,
                mission_id=mission_id,
                status=MissionStatus.COMPLETED,
                score=score_value
            )

            self.missions_repo.add(progress)
            self.uow.commit()
        return progress