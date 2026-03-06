from server.app.domain.errors import NotFoundError

class FetchEdgeData:
    def __init__(self, graph_data_repo):
        self.graph_data_repo = graph_data_repo

    def execute(self, edge_id):
        edge = self.graph_data_repo.get_edge_by_id(edge_id)
        if not edge:
            raise NotFoundError(message="Edge not found")
        return edge