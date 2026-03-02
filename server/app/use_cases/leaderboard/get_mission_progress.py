from server.app.domain.errors import NotFoundError

class GetMissionProgress:
    def __init__(self, leaderboard_repo):
        self.leaderboard_repo = leaderboard_repo

    def execute(self, user_id, mission_id):
        progress = self.leaderboard_repo.get_progress_by_id(user_id, mission_id)
        if not progress:
            raise NotFoundError(message="Mission not found")
        return progress
