from server.app.models.missions_model import MissionsModel
from server.app.models.mission_progress_model import MissionProgressModel
from server.app.repositories.db_error_mapper import map_db_errors
from sqlalchemy import select

class LeaderboardRepository:
    def __init__(self, session):
        self.session = session

    @map_db_errors("leaderboard:get_all")
    def get_all(self):
        stmt = select(MissionProgressModel)
        results = self.session.execute(stmt).scalars().all()
        return results

    @map_db_errors("leaderboard:get_by_id")
    def get_progress_by_id(self, user_id, mission_id):
        stmt = select(MissionProgressModel).where((MissionProgressModel.mission_id == mission_id) & (MissionProgressModel.user_id == user_id))
        return self.session.execute(stmt).scalars().first()
    
    def add(self, progress: MissionProgressModel):
        self.session.add(progress)

    def delete(self, progress: MissionProgressModel):
        self.session.delete(progress)
        self.session.commit()
