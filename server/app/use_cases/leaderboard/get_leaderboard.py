from app.domain.errors import NotFoundError

class GetLeaderboard:
    def __init__(self, leaderboard_repo):
        self.leaderboard_repo = leaderboard_repo

    def execute(self):
        progress = self.leaderboard_repo.get_all()
        if not progress:
            raise NotFoundError(message="Leaderboard not found")
        return progress
