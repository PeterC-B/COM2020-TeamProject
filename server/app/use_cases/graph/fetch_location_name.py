from app.domain.errors import NotFoundError

class FetchLocationName:
    def __init__(self, graph_data_repo):
        self.graph_data_repo = graph_data_repo

    def execute(self, node_id):
        name = self.graph_data_repo.get_location_name(node_id)
        if not name:
            raise NotFoundError(message="Name not found")
        return name
        
