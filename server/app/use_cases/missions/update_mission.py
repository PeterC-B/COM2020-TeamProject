from server.app.domain.errors import NotFoundError
from server.app.models.missions_model import MissionsModel


class UpdateMission:
    def __init__(self, uow, missions_repo):
        self.uow = uow
        self.missions_repo = missions_repo

    def execute(self, mission_id, payload: dict) -> MissionsModel:
        with self.uow:
            mission = self.missions_repo.get_by_id(mission_id)

            if mission is None:
                raise NotFoundError(message="Mission not found")

            # Update allowed fields only
            for field in [
                "mission_name",
                "question",
                "possible_answers",
                "answer",
                "tier",
            ]:
                if field in payload:
                    setattr(mission, field, payload[field])

            self.uow.commit()

        return mission
