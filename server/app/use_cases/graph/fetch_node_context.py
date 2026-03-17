from app.domain.errors import NotFoundError

class FetchNodeContext:
    def __init__(self, graph_data_repo):
        self.graph_data_repo = graph_data_repo

    def execute(self, node_id):
        node = self.graph_data_repo.fetch_node_context(node_id)
        if not node:
            raise NotFoundError(message="Node not found")
        return node