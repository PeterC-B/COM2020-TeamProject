class ListRouteQueries:
    def __init__(self, repo):
        self.repo = repo

    def execute(self):
        return self.repo.list_all()
