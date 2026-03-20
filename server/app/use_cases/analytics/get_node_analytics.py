from app.repositories.graph_data_repository import GraphDataRepository
from app.extensions import db
from app.api.error_handlers import NotFoundError

class GetNodeAnalytics:
    def __init__(self, analytics_repo):
        self.analytics_repo = analytics_repo

    def execute(self):
        try:
            graph_repo = GraphDataRepository(db.session)
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

            return data
        except Exception as e:
            print("Error:", e)
            raise NotFoundError(message=str(e))