from app.models.missions_model import MissionsModel
from app.models.mission_progress_model import MissionProgressModel
from app.repositories.db_error_mapper import map_db_errors
from sqlalchemy import select

class AnalyticsRepository:
    def __init__(self, session):
        self.session = session

    @map_db_errors("analytics:get_all")
    def get_mission_analytics(self):
        stmt = (
            select(MissionProgressModel, MissionsModel)
            .join(MissionsModel, MissionProgressModel.mission_id == MissionsModel.mission_id)
        )
        results = self.session.execute(stmt).all()
        return results