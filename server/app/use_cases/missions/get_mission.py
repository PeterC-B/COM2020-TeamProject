from app.domain.errors import NotFoundError


class GetMission:
    def __init__(self, missions_repo):
        self.missions_repo = missions_repo

    def execute(self, mission_id):
        mission = self.missions_repo.get_by_id(mission_id)
        if not mission:
            raise NotFoundError(message="Mission not found")
        return mission
