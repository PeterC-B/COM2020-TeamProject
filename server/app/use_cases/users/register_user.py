

import datetime
from dataclasses import dataclass

from app.models.user_account_model import UserAccountModel


@dataclass(frozen=True)
class RegisterUserResult:
    user_id: str


class RegisterUser:
    def __init__(self, uow, user_repo):
        self.uow = uow
        self.user_repo = user_repo

    def execute(self, payload: dict) -> RegisterUserResult:
        
        first_name = payload.get('first_name')
        last_name = payload.get('last_name')
        password = payload.get('password')

        created_at = datetime.datetime.now(tz=datetime.timezone.utc)

        # Hash password simply here for now but will move to a service later
        hashed_password = f"hashed-{password}"

        with self.uow:

            user = UserAccountModel(
                first_name=first_name,
                last_name=last_name,
                password_hash=hashed_password,
                created_at=created_at
            )

            self.user_repo.add(user)

            self.uow.commit()

        return RegisterUserResult(user_id=str(user.id))