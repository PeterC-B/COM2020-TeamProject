"""Routing API endpoint for Yen's algorithm."""

from server.app.api.responses import ok
from flask import Blueprint, request
from server.app.api.error_handlers import ValidationError

def create_routing_route_blueprint(route_yens_uc):
    bp = Blueprint("routing", __name__, url_prefix="/api/routing")

    @bp.route("", methods=["POST"])
    def route_yens():
        try:
            data = request.get_json(silent=True)
            payload, status = route_yens_uc.execute(data)
            return ok(data=payload, status=status)
        except Exception as e:
            print(f"Error: {e}")
            raise(ValidationError(message=e))

    return bp
