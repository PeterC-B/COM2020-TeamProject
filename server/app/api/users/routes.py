# Holds the routes for user-related operations

from flask import Blueprint, request

from app.schemas.user.user_read import UserReadSchema
from app.schemas.user.user_register import UserRegisterSchema


def create_user_route_blueprint(register_user_uc, list_users_uc):
    bp = Blueprint("user", __name__, url_prefix="/user")

    @bp.route("/register", methods=["POST"])
    def register_user():
        # Validate with schema
        payload = UserRegisterSchema().load(request.get_json())
        # Call use case to perform the logic
        result = register_user_uc.execute(payload)
        return {"message": "User registered successfully", "data": result}, 201
    
    @bp.route("/list", methods=["GET"])
    def list_users():
        # Call use case to get users
        result = list_users_uc.execute()

        # Validate output with Schema
        data = UserReadSchema(many=True).dump(result.items)

        return {"message": "Users retrieved successfully", "data": data}, 200

    return bp
