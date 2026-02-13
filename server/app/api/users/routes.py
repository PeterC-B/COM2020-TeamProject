# Holds the routes for user-related operations

from app.api.responses import created, ok
from app.schemas.user.user_read import UserReadSchema
from app.schemas.user.user_register import UserRegisterSchema
from flask import Blueprint, request


def create_user_route_blueprint(register_user_uc, list_users_uc, login_user_uc):
    bp = Blueprint("user", __name__, url_prefix="/user")

    @bp.route("/register", methods=["POST"])
    def register_user():
        # Validate with schema
        payload = UserRegisterSchema().load(request.get_json())

        # Call use case to perform the logic
        print("Executing registration")
        result = register_user_uc.execute(payload)
        return created(
            data={"user_id": result.user_id},
            meta={"created": True},
        )
    
    @bp.route("/list", methods=["GET"])
    def list_users():
        # Call use case to get users
        result = list_users_uc.execute()

        # Validate output with Schema
        data = UserReadSchema(many=True).dump(result.items)
        meta = {
            "total": result.total,
        }
        return ok(data=data, meta=meta)

    @bp.route("/login", methods=["POST"])
    def login_user():
        payload = request.get_json(silent=True) or {}
        print('Executing login')
        result = login_user_uc.execute(payload)
        return ok(
            data={
                "access_token": result.access_token,
                "role": result.role,
                "username": result.username,
            }
        )
    
    return bp
