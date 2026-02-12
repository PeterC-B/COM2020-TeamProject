

import datetime
from dataclasses import dataclass

from server.app.domain.errors import ValidationError
from server.app.models.enums.ACCESS_TYPE import UserAccessType
from server.app.models.user_account_model import UserAccountModel


@dataclass(frozen=True)
class RegisterUserResult:
    user_id: str


class RegisterUser:
    def __init__(self, uow, user_repo):
        self.uow = uow
        self.user_repo = user_repo

    def execute(self, payload: dict) -> RegisterUserResult:
        
        username = payload.get('username')
        email = payload.get('email')
        password = payload.get('password')
        role = payload.get('role')

        created_at = datetime.datetime.now(tz=datetime.timezone.utc)

        # Hash password simply here for now but will move to a service later
        hashed_password = f"hashed-{password}"

        role_map = {
            "travellers": UserAccessType.TRAVELLERS,
            "administrators": UserAccessType.ADMINS,
            "developers": UserAccessType.MAINTAINERS,
        }
        role_enum = role_map.get((role or "travellers").lower())
        if role_enum is None:
            raise ValidationError(message="Invalid role value")

        with self.uow:

            user = UserAccountModel(
                username=username,
                email=email,
                password_hash=hashed_password,
                role=role_enum,
                created_at=created_at
            )

            self.user_repo.add(user)

            self.uow.commit()

        return RegisterUserResult(user_id=str(user.user_id))
