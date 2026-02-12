from server.app.models.missions_model import MissionsModel

class CreateMission:
    def __init__(self, uow, missions_repo):
        self.uow = uow
        self.missions_repo = missions_repo


    def execute(self, payload):
        mission = MissionsModel(**payload)
        self.missions_repo.add(mission)
        self.uow.commit()
        return mission