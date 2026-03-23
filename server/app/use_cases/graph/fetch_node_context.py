from app.domain.errors import NotFoundError

class FetchNodeContext:
    def __init__(self, graph_data_repo):
        self.graph_data_repo = graph_data_repo

    def execute(self, node_id):
        context = self.graph_data_repo.fetch_node_context(node_id)
        if not context:
            raise NotFoundError(message="Context not found")
        
        node, location = context
        return {
            "node_id": node.node_id,
            "coordinates": (node.x_coordinate, node.y_coordinate),
            "nodeType": location.information,
            "name": location.name,
            "highway": node.feature
        }