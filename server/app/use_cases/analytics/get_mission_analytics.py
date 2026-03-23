from app.domain.errors import NotFoundError

class GetMissionAnalytics:
    def __init__(self, analytics_repo):
        self.analytics_repo = analytics_repo

    def execute(self):
        rows = self.analytics_repo.get_mission_analytics()
        if not rows:
            raise NotFoundError(message="Analytics data not found")
        
        return [{
                "mission_id": mission.mission_id,
                "mission_name": mission.mission_name,
                "status": progress.status.value,
                "chosen_answer": progress.chosenAnswer,
                "score": progress.score,
                "user_id": progress.user_id
            }
            for progress, mission in rows
        ]