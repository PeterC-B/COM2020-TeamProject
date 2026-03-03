# Provides data access methods for user entities
# Very strict and thin layer focused purely on database operations
import uuid
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
    
    @map_db_errors("user:get_by_email")
    def get_by_email(self, email: str):
        stmt = select(UserAccountModel).where(UserAccountModel.email == email)
        return self.session.execute(stmt).scalars().first()

    @map_db_errors("user:update_password")
    def update_password(self, user_id: uuid.UUID, new_hash: str):
        user = self.session.get(UserAccountModel, user_id)
        user.password_hash = new_hash
        self.session.add(user)

