from app.models.missions_model import MissionsModel
from sqlalchemy import select


class MissionsRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self):
        stmt = select(MissionsModel)
        results = self.session.execute(stmt).scalars().all()
        return results

    def get_by_id(self, mission_id):
        stmt = select(MissionsModel).where(MissionsModel.mission_id == mission_id)
        return self.session.execute(stmt).scalars().first()
        return self.session.execute(stmt).scalars().first()
