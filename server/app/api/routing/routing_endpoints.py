"""Routing API endpoint for Yen's algorithm."""

from flask import Blueprint, jsonify, request

from server.app.domain.routing.algorithms.yen_algorithm import process_yens_routing_request


def create_routing_route_blueprint():
    bp = Blueprint("routing", __name__, url_prefix="/routing")

    @bp.route("", methods=["POST"])
    def route_yens():
        data = request.get_json(silent=True)
        payload, status = process_yens_routing_request(data)
        return jsonify(payload), status

    return bp
