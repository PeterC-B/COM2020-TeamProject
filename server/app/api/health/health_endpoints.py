"""Health endpoints."""

from flask import Blueprint, jsonify, request


def create_health_routes(get_health_attributes_uc, get_default_weights_uc, explain_edge_cost_uc):
    health_bp = Blueprint("health", __name__, url_prefix="/health")

    @health_bp.route("/attributes", methods=["GET"])
    def get_attributes():
        return jsonify(get_health_attributes_uc.execute())

    @health_bp.route("/weights/defaults", methods=["GET"])
    def get_default_weights():
        return jsonify(get_default_weights_uc.execute())

    @health_bp.route("/explain", methods=["POST"])
    def explain_cost():
        data = request.get_json(silent=True)
        return jsonify(explain_edge_cost_uc.execute(data))

    return health_bp
