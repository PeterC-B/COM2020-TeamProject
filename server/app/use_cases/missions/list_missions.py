class ListMissions:
    def __init__(self, missions_repo):
        self.missions_repo = missions_repo

    def execute(self):
        return self.missions_repo.get_all()
