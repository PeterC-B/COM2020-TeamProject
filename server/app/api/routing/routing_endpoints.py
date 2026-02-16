"""Routing API endpoint for Yen's algorithm."""

from app.api.responses import ok
from flask import Blueprint, request


def create_routing_route_blueprint(route_yens_uc):
    bp = Blueprint("routing", __name__, url_prefix="/api/routing")

    @bp.route("", methods=["POST"])
    def route_yens():
        data = request.get_json(silent=True)
        payload, status = route_yens_uc.execute(data)
        return ok(data=payload, status=status)

    return bp
