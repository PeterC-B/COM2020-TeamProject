from app.repositories.graph_data_repository import GraphDataRepository
from app.extensions import db
from app.api.error_handlers import NotFoundError

class GetEdgeAnalytics:
    def __init__(self, analytics_repo):
        self.analytics_repo = analytics_repo

    def execute(self):    
        try:
            graph_repo = GraphDataRepository(db.session)
            edges = graph_repo.get_all_edges()

            data = [
                {
                    "edge_id": e.edge_id,
                    "from_node": e.from_node_id,
                    "to_node": e.to_node_id,
                    "length": e.length,
                    "travel_time": e.travel_time,
                    "is_accessible": e.is_accessible,
                    "lighting": e.lighting,
                    "greenery": e.greenery,
                    "pollution": e.pollution,
                    "surface_quality": e.surface_quality,
                    "pub_distance": e.pub_distance,
                }
                for e in edges
            ]

            return data
        except Exception as e:
            print("Error:", e)
            raise NotFoundError(message=str(e))