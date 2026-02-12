# Provides data access methods for user entities
# Very strict and thin layer focused purely on database operations

from sqlalchemy import select

from app.models.user_account_model import UserAccountModel


class UserRepository:
    def __init__(self, session):
        self.session = session

    def add(self, user: UserAccountModel) -> None:
        self.session.add(user)


    def get(self):
        stmt = select(UserAccountModel)

        results = self.session.execute(stmt).scalars().all()

        return results, len(results)

    def get_by_username(self, username: str):
        stmt = select(UserAccountModel).where(UserAccountModel.username == username)
        response = self.session.execute(stmt).scalars().first()
        return response
