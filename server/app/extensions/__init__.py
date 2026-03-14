from functools import wraps

from flask_jwt_extended import (
    JWTManager,
    verify_jwt_in_request,
    current_user
)
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()

from app.models.user_account_model import UserAccountModel
from app.models.enums.ACCESS_TYPE import UserAccessType

@jwt.user_lookup_loader
def load_user(jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return db.session.get(UserAccountModel, identity)

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if current_user.role != UserAccessType.ADMIN:
            return {"error": "Forbidden", "message": "Admin access required"}, 403
        return fn(*args, **kwargs)
    return wrapper
