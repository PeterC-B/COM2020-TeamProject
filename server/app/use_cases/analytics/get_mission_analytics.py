from app.domain.errors import NotFoundError

class GetMissionAnalytics:
    def __init__(self, analytics_repo):
        self.analytics_repo = analytics_repo

    def execute(self):
        progress = self.analytics_repo.get_mission_analytics()
        if not progress:
            raise NotFoundError(message="Analytics data not found")
        return progress