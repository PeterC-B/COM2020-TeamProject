class ListGraphPresets:
    def __init__(self, graph_data_repo):
        self.graph_data_repo = graph_data_repo

    def execute(self):
        self.graph_data_repo.ensure_default_presets()
        return self.graph_data_repo.list_graph_presets()
