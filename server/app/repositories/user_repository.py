# Provides data access methods for user entities
# Very strict and thin layer focused purely on database operations

from sqlalchemy import select

from server.app.models.user_account_model import UserAccountModel
from server.app.repositories.db_error_mapper import map_db_errors


class UserRepository:
    def __init__(self, session):
        self.session = session

    def add(self, user: UserAccountModel) -> None:
        self.session.add(user)

    @map_db_errors("user:get")
    def get(self):
        stmt = select(UserAccountModel)

        results = self.session.execute(stmt).scalars().all()

        return results, len(results)

    @map_db_errors("user:get_by_username")
    def get_by_username(self, username: str):
        stmt = select(UserAccountModel).where(UserAccountModel.username == username)
        return self.session.execute(stmt).scalars().first()
