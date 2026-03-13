from app.domain.errors import NotFoundError, ValidationError


class ActivateGraphPreset:
    def __init__(self, graph_data_repo):
        self.graph_data_repo = graph_data_repo

    def execute(self, preset_code):
        self.graph_data_repo.ensure_default_presets()
        preset = self.graph_data_repo.get_graph_preset_by_code(preset_code)
        if not preset:
            raise NotFoundError(message="Preset location not found")

        snapshot = preset.get("snapshot")
        if not snapshot or not isinstance(snapshot, dict):
            raise ValidationError(message="Preset snapshot not found")

        features = snapshot.get("features")
        if not isinstance(features, dict):
            raise ValidationError(message="Preset snapshot is invalid")

        self.graph_data_repo.load_graph_features(features)
        return snapshot
