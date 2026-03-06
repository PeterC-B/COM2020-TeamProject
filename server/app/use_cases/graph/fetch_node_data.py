from server.app.domain.errors import NotFoundError

class FetchNodeData:
    def __init__(self, graph_data_repo):
        self.graph_data_repo = graph_data_repo

    def execute(self, node_id):
        node = self.graph_data_repo.get_node_by_id(node_id)
        if not node:
            raise NotFoundError(message="Node not found")
        return node