from app.domain.errors import NotFoundError


class GetGraphPresetSnapshot:
    def __init__(self, graph_data_repo):
        self.graph_data_repo = graph_data_repo

    def execute(self, preset_code):
        self.graph_data_repo.ensure_default_presets()
        snapshot = self.graph_data_repo.get_graph_preset_snapshot(preset_code)
        if snapshot is None:
            raise NotFoundError(message="Preset snapshot not found")
        return snapshot
