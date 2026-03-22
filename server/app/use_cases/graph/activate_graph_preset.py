from app.domain.errors import NotFoundError, ValidationError
from app.use_cases.graph.get_graph_data_for_coords import FetchDataForCoordinates

class ActivateGraphPreset:
    def __init__(self, uow, graph_data_repo):
        self.graph_data_repo = graph_data_repo
        self.uow = uow

    def execute(self, preset_code):
        self.graph_data_repo.ensure_default_presets()
        preset = self.graph_data_repo.get_graph_preset_by_code(preset_code)
        if not preset:
            raise NotFoundError(message="Preset location not found")

        snapshot = preset["snapshot"]

        if not snapshot or not isinstance(snapshot, dict):
            fetcher = FetchDataForCoordinates(
                uow=self.uow,
                graph_data_repo=self.graph_data_repo
            )

            snapshot = fetcher.execute(
                coords=(preset["lat"], preset["lon"])
            )
            self.graph_data_repo.upsert_graph_preset_snapshot(preset["code"], snapshot)
        
        features = snapshot["features"]

        if features["nodes"]["features"] == [] or features["edges"]["features"] == [] or features["locations"]["features"] == [] or features["center"] is None:
            fetcher = FetchDataForCoordinates(
                uow=self.uow,
                graph_data_repo=self.graph_data_repo
            )

            snapshot = fetcher.execute(
                coords=(preset["lat"], preset["lon"])
            )
            self.graph_data_repo.upsert_graph_preset_snapshot(preset["code"], snapshot)
        
        try:
            self.graph_data_repo.load_graph_features(features)
            return snapshot
        except:
            try:
                fetcher = FetchDataForCoordinates(
                    uow=self.uow,
                    graph_data_repo=self.graph_data_repo
                )

                new_snapshot = fetcher.execute(
                    coords=(preset["lat"], preset["lon"])
                )
                self.graph_data_repo.upsert_graph_preset_snapshot(preset["code"], new_snapshot)
                self.graph_data_repo.load_graph_features(new_snapshot["features"])
                
                return new_snapshot
            except Exception as e:
                raise ValidationError(message=e)