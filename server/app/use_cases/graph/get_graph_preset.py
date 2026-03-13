from app.domain.errors import NotFoundError


class GetGraphPreset:
    def __init__(self, graph_data_repo):
        self.graph_data_repo = graph_data_repo

    def execute(self, preset_code):
        self.graph_data_repo.ensure_default_presets()
        preset = self.graph_data_repo.get_graph_preset_by_code(preset_code)
        if not preset:
            raise NotFoundError(message="Preset location not found")
        return preset
