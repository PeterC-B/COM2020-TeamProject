from app.domain.errors import NotFoundError


class DeleteMission:
    def __init__(self, uow, missions_repo):
        self.uow = uow
        self.missions_repo = missions_repo

    def execute(self, mission_id):
        with self.uow:
            mission = self.missions_repo.get_by_id(mission_id)
            mission_progress = self.missions_repo.get_mission_progress_for_mission(mission_id)
            if not mission:
                raise NotFoundError(message="Mission not found")
            if mission_progress:
                for progress in mission_progress:
                    self.missions_repo.delete(progress)
            self.missions_repo.delete(mission)