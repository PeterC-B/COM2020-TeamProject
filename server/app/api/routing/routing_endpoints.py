"""Routing API endpoint for Yen's algorithm."""

from flask import Blueprint, jsonify, request

def create_routing_route_blueprint(route_yens_uc):
    bp = Blueprint("routing", __name__, url_prefix="/routing")

    @bp.route("", methods=["POST"])
    def route_yens():
        data = request.get_json(silent=True)
        payload, status = route_yens_uc.execute(data)
        return jsonify(payload), status

    return bp
