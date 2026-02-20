from server.app.domain.errors import NotFoundError


class DeleteMission:
    def __init__(self, uow, missions_repo):
        self.uow = uow
        self.missions_repo = missions_repo

    def execute(self, mission_id):
        with self.uow:
            mission = self.missions_repo.get_by_id(mission_id)
            if not mission:
                raise NotFoundError(message="Mission not found")
            self.missions_repo.delete(mission)