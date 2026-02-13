from dataclasses import dataclass

from flask_jwt_extended import create_access_token

from server.app.domain.errors import AuthError, ValidationError


@dataclass(frozen=True)
class LoginUserResult:
    access_token: str
    role: str
    username: str


class LoginUser:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, payload: dict) -> LoginUserResult:
        username = payload.get("username")
        password = payload.get("password")

        print("Username and password received:", username, password)

        if not username or not password:
            raise ValidationError(message="Username and password are required")

        
        user = self.user_repo.get_by_username(username)
        if user is None or user.password_hash != f"hashed-{password}":
            raise AuthError(message="Invalid username or password")

        access_token = create_access_token(identity=str(user.user_id))
        return LoginUserResult(
            access_token=access_token,
            role=user.role.value,
            username=user.username,
        )
