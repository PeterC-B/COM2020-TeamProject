from app.api.responses import ok
from flask import Blueprint


def create_graph_route_blueprint(get_graph_data_uc):
    bp = Blueprint("graph", __name__, url_prefix="/api/graph")

    @bp.route("", methods=["GET"])
    def get_graph_data():
        return ok(data=get_graph_data_uc.execute())

    return bp
