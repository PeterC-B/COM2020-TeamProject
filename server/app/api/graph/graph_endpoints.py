from flask import Blueprint, jsonify


def create_graph_route_blueprint(get_graph_data_uc):
    bp = Blueprint("graph", __name__, url_prefix="/graph")

    @bp.route("", methods=["GET"])
    def get_graph_data():
        return jsonify(get_graph_data_uc.execute())

    return bp
