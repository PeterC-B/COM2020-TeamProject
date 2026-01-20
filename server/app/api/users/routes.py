# Holds the routes for user-related operations

from flask import Blueprint


def create_user_route_blueprint(register_user_uc):
    bp = Blueprint("user", __name__, url_prefix="/user")

    @bp.route("/register", methods=["POST"])
    def register_user():
        # Validate with schema
        # Call use case to register user
        result = register_user_uc.execute()

        # Validate output with Schema

        return {"message": "User registered successfully", "data": result}, 201
    
    
    return bp
