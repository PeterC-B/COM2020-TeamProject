from server.app.models.enums.MISSION_TIER import MissionTier
from server.app.models.enums.MISSION_STATUS import MissionStatus
from server.app.models.mission_progress_model import MissionProgressModel
from server.app.domain.errors import ValidationError
import uuid


class SaveMissionProgress:
    def __init__(self, uow, leaderboard_repo):
        self.uow = uow
        self.leaderboard_repo = leaderboard_repo


    def execute(self, payload):
        try:
            user_id = uuid.UUID(payload.get("user_id"))
            mission_id = uuid.UUID(payload.get("mission_id"))
        except ValueError:
            raise ValidationError(message="Invalid UUID format")
        
        status = payload.get('status')
        tier = payload.get('tier')

        print(user_id, mission_id, status, tier)

        missing = [
            field for field, value in {
                "user_id": user_id,
                "mission_id": mission_id,
                "status": status,
                "tier": tier,
            }.items() if not value
        ]

        if missing:
            raise ValidationError(
                message="Missing required fields",
                details={"missing": missing}
            )

        score_map = {
            "EASY": 10,
            "MEDIUM": 20,
            "HARD": 30,
        }

        completion_map = {
            "correct": MissionStatus.CORRECT,
            "incorrect": MissionStatus.INCORRECT,
        }

        score_value = score_map.get(tier, 0)
        
        status_value = completion_map.get((status or "incorrect").lower())

        if(status == "correct"):
            status_value = MissionStatus.CORRECT

        with self.uow:

            progress = MissionProgressModel(
                user_id=user_id,
                mission_id=mission_id,
                status=status_value,
                score=score_value
            )

            self.leaderboard_repo.add(progress)
            self.uow.commit()
        return progress