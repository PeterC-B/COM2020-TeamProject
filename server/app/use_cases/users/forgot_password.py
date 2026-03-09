from dataclasses import dataclass
from app.domain.errors import ValidationError
from app.security.passwords import hash_password
@dataclass(frozen=True)
class ForgotPasswordResult:
    reset: bool

class ForgotPassword:
    def __init__(self, uow, user_repo):
        self.uow = uow
        self.user_repo = user_repo

    def execute(self, username: str, email: str, new_password: str) -> ForgotPasswordResult:
        if not username or not email or not new_password:
            raise ValidationError("All fields are required")

        user = self.user_repo.get_by_username(username)

        if user is None or user.email != email:
            raise ValidationError("Username and email do not match")

        new_hash = hash_password(new_password)
        self.user_repo.update_password(user.user_id, new_hash)

        self.uow.commit()

        return ForgotPasswordResult(reset=True)
