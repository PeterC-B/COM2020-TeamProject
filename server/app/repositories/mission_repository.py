from app.models.missions_model import MissionsModel
from app.repositories.db_error_mapper import map_db_errors
from sqlalchemy import select


class MissionsRepository:
    def __init__(self, session):
        self.session = session

    @map_db_errors("missions:get_all")
    def get_all(self):
        stmt = select(MissionsModel)
        results = self.session.execute(stmt).scalars().all()
        return results

    @map_db_errors("missions:get_by_id")
    def get_by_id(self, mission_id):
        stmt = select(MissionsModel).where(MissionsModel.mission_id == mission_id)
        return self.session.execute(stmt).scalars().first()
