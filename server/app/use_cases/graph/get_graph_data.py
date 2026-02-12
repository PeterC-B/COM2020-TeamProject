class GetGraphData:
    def __init__(self, graph_data_repo):
        self.graph_data_repo = graph_data_repo

    def execute(self):
        return {"features": self.graph_data_repo.get_graph_features()}
