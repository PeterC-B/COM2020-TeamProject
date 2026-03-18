from flask import Blueprint
from app.api.responses import ok
from app.api.error_handlers import NotFoundError
from app.repositories.graph_data_repository import GraphDataRepository
from app.extensions import db

def create_analytics_blueprint(get_mission_analytics_uc):
    bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

    # Create the repository here
    graph_repo = GraphDataRepository(db.session)

    @bp.route("/missions", methods=["GET"])
    def get_mission_analytics():
        try:
            analytics = get_mission_analytics_uc.execute()
            return ok(data=analytics)
        except Exception as e:
            print("Error:", e)
            raise NotFoundError(message=str(e))

    @bp.route("/nodes", methods=["GET"])
    def get_node_analytics():
        try:
            nodes = graph_repo.get_all_nodes()
            locations = graph_repo.get_used_locations()

            location_map = {loc.node_id: loc for loc in locations}

            data = []
            for n in nodes:
                loc = location_map.get(n.node_id)

                name = loc.name if loc else "Unnamed Node"
                type_ = loc.information if loc else (n.feature or "Unknown")

                data.append({
                    "node_id": n.node_id,
                    "name": name,
                    "type": type_,
                    "lat": n.y_coordinate,
                    "lon": n.x_coordinate,
                })

            return ok(data=data)
        except Exception as e:
            print("Error:", e)
            raise NotFoundError(message=str(e))

    @bp.route("/edges", methods=["GET"])
    def get_edge_analytics():
        try:
            edges = graph_repo.get_all_edges()

            data = [
                {
                    "edge_id": e.edge_id,
                    "from_node": e.from_node_id,
                    "to_node": e.to_node_id,
                    "length": e.length,
                    "travel_time": e.travel_time,
                    "access_score": e.access_score,
                    "lighting": e.lighting,
                    "greenery": e.greenery,
                    "pollution": e.pollution,
                    "surface_quality": e.surface_quality,
                    "pub_distance": e.pub_distance,
                }
                for e in edges
            ]

            return ok(data=data)
        except Exception as e:
            print("Error:", e)
            raise NotFoundError(message=str(e))

    return bp
