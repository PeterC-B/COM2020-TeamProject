from app.models.enums.MISSION_TIER import MissionTier
from app.models.enums.MISSION_STATUS import MissionStatus
from app.models.mission_progress_model import MissionProgressModel
from app.domain.errors import ValidationError
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
        score = payload.get('score')
        chosen_answer = payload.get('chosen_answer')

        missing = [
            field for field, value in {
                "user_id": user_id,
                "mission_id": mission_id,
                "status": status,
                "score": score,
                "chosen_answer": chosen_answer
            }.items() if not value
        ]

        if missing:
            raise ValidationError(
                message="Missing required fields",
                details={"missing": missing}
            )

        completion_map = {
            "correct": MissionStatus.CORRECT,
            "incorrect": MissionStatus.INCORRECT,
        }
        
        status_value = completion_map.get((status or "incorrect").lower())

        with self.uow:

            progress = MissionProgressModel(
                user_id=user_id,
                mission_id=mission_id,
                status=status_value,
                score=score,
                chosenAnswer=chosen_answer
            )

            self.leaderboard_repo.add(progress)
            self.uow.commit()
        return progress