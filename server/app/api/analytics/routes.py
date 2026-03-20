from flask import Blueprint
from app.api.responses import ok
from app.api.error_handlers import NotFoundError
from app.repositories.graph_data_repository import GraphDataRepository
from app.extensions import db

def create_analytics_blueprint(get_mission_analytics_uc, get_node_analytics_uc, get_edge_analytics_uc):
    bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

    # Create the repository here
    graph_repo = GraphDataRepository(db.session)

    @bp.route("/missions", methods=["GET"])
    def get_mission_analytics():
        try:
            analytics = get_mission_analytics_uc.execute()
            return ok(data=analytics)
        except Exception as e:
            print("Error", e)
            raise NotFoundError(message=str(e))

    @bp.route("/nodes", methods=["GET"])
    def get_node_analytics():
        analytics = get_node_analytics_uc.execute()
        return ok(data=analytics)

    @bp.route("/edges", methods=["GET"])
    def get_edge_analytics():
        try:
            analytics = get_edge_analytics_uc.execute()
            return ok(data=analytics)
        except Exception as e:
            print("Error:", e)
            raise NotFoundError(e)

    return bp
