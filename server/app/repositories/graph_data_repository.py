import uuid
from pathlib import Path

from sqlalchemy import select

from app.data.convert import build_edges_geojson, build_locations_geojson, build_nodes_geojson
from app.models.edges_model import EdgesModel
from app.models.enums.LOCATION_TYPE import LocationType
from app.models.graph_preset_model import GraphPresetModel
from app.models.location_model import LocationModel
from app.models.nodes_model import NodesModel

DEFAULT_GRAPH_PRESETS = [
    {"preset_code": "bristol", "name": "Bristol", "latitude": 51.4545, "longitude": -2.5879},
    {"preset_code": "liverpool", "name": "Liverpool", "latitude": 53.4084, "longitude": -2.9916},
    {"preset_code": "exeter", "name": "Exeter", "latitude": 50.7184, "longitude": -3.5339},
    {"preset_code": "basingstoke", "name": "Basingstoke", "latitude": 51.2665, "longitude": -1.0924},
    {"preset_code": "manchester", "name": "Manchester", "latitude": 53.4808, "longitude": -2.2426},
    {"preset_code": "birmingham", "name": "Birmingham", "latitude": 52.4862, "longitude": -1.8904},
    {"preset_code": "leeds", "name": "Leeds", "latitude": 53.8008, "longitude": -1.5491},
    {"preset_code": "nottingham", "name": "Nottingham", "latitude": 52.9548, "longitude": -1.1581},
    {"preset_code": "cardiff", "name": "Cardiff", "latitude": 51.4816, "longitude": -3.1791},
    {"preset_code": "southampton", "name": "Southampton", "latitude": 50.9097, "longitude": -1.4044},
]


class GraphDataRepository:
    def __init__(self, session, data_path: Path | None = None):
        self.session = session
        self.data_path = data_path or Path("app/data/processed")

    def get_graph_features(self):
        nodes_list = self.get_all_nodes()
        edges_list = self.get_all_edges()
        locations_list = self.get_used_locations()
        centre = self.get_graph_center()

        nodes_geojson = build_nodes_geojson(nodes_list)
        edges_geojson = build_edges_geojson(edges_list)
        location_geojson = build_locations_geojson(locations_list, nodes_list)
    
        return {
            "nodes": nodes_geojson,
            "edges": edges_geojson,
            "locations": location_geojson,
            "center": centre,
        }

    def get_graph_center(self) -> tuple[float, float] | None:
        nodes = self.get_all_nodes()
        if not nodes:
            return None

        sum_lat = 0.0
        sum_lon = 0.0
        count = 0

        for node in nodes:
            if node.x_coordinate is not None and node.y_coordinate is not None:
                sum_lat += node.x_coordinate
                sum_lon += node.y_coordinate
                count += 1

        if count == 0:
            return None

        center_lat = sum_lat / count
        center_lon = sum_lon / count
        return (center_lon, center_lat)

    def bulk_add(self, objects):
        self.session.bulk_save_objects(objects)

    def get_nodes_by_location(self, locations):
        node_ids = [location.node_id for location in locations]
        print(node_ids)
        return self.session.query(NodesModel).filter(
            NodesModel.node_id.in_(node_ids)
        ).all()

    def get_edge_by_id(self, edge_id):
        stmt = select(EdgesModel).where(EdgesModel.edge_id == edge_id)
        return self.session.execute(stmt).scalars().first()

    def get_all_edges(self) -> list:
        return self.session.query(EdgesModel).all()

    def get_all_nodes(self) -> list:
        return self.session.query(NodesModel).all()

    def get_all_locations(self) -> list:
        stmt = select(LocationModel).where(LocationModel.name != "NaN")
        return self.session.execute(stmt).scalars().all()

    def get_location_name(self, node_id):
        stmt = select(LocationModel.name).where(LocationModel.node_id == node_id)
        print(node_id)
        return self.session.execute(stmt).scalars().first()

    def get_used_locations(self) -> list:
        stmt = (
            select(LocationModel)
            .join(NodesModel, LocationModel.node_id == NodesModel.node_id)
            .where(LocationModel.name != "NaN")
        )
        return self.session.execute(stmt).scalars().all()

    def get_node_by_id(self, node_id):
        stmt = select(NodesModel).where(NodesModel.node_id == node_id)
        return self.session.execute(stmt).scalars().first()

    def clear_tables(self):
        self.session.query(LocationModel).delete()
        self.session.query(EdgesModel).delete()
        self.session.query(NodesModel).delete()
        self.session.commit()

    def load_graph_features(self, features):
        if not isinstance(features, dict):
            return

        nodes_fc = features["nodes"]
        edges_fc = features["edges"]
        locations_fc = features["locations"]

        node_features = nodes_fc["features"] if isinstance(nodes_fc, dict) else []
        edge_features = edges_fc["features"] if isinstance(edges_fc, dict) else []
        location_features = locations_fc["features"] if isinstance(locations_fc, dict) else []

        nodes_to_add = []
        for feature in node_features:
            geometry = feature["geometry"]
            coordinates = geometry["coordinates"]
            properties = feature["properties"]
            if len(coordinates) < 2:
                continue

            node_id = properties["node_id"]
            if node_id is None:
                continue

            nodes_to_add.append(
                NodesModel(
                    node_id=int(node_id),
                    x_coordinate=float(coordinates[0]),
                    y_coordinate=float(coordinates[1]),
                    feature=properties["highway"],
                )
            )

        edges_to_add = []
        for feature in edge_features:
            geometry = feature["geometry"]
            coordinates = geometry["coordinates"]
            properties = feature["properties"]
            if len(coordinates) < 2:
                continue

            edge_id = properties["edge_id"]
            from_node = properties["from_node"]
            to_node = properties["to_node"]
            if edge_id is None or from_node is None or to_node is None:
                continue

            edges_to_add.append(
                EdgesModel(
                    edge_id=int(edge_id),
                    from_node_id=int(from_node),
                    to_node_id=int(to_node),
                    key=int(properties["key"]),
                    length=float(properties["length"]),
                    travel_time=float(properties["travel_time"]),
                    access_score=float(properties["access_score"]),
                    geometry=self._linestring_to_wkt(coordinates),
                    lighting=float(properties["lighting"]),
                    greenery=float(properties["greenery"]),
                    pollution=float(properties["pollution"]),
                    surface_quality=float(properties["surface_quality"]),
                    pub_distance=float(properties["pub_distance"]),
                )
            )

        locations_to_add = []
        for feature in location_features:
            properties = feature["properties"]
            node_id = properties["node_id"]
            if node_id is None:
                continue

            name = str(properties["name"]).strip()
            if not name:
                name = "Unnamed Amenity"

            info = properties["type"]
            locations_to_add.append(
                LocationModel(
                    location_id=uuid.uuid4(),
                    name=name,
                    node_id=int(node_id),
                    type=LocationType.GENERAL_AMENITY,
                    information=str(info) if info is not None else None,
                    in_use=True,
                )
            )

        self.clear_tables()

        if nodes_to_add:
            self.bulk_add(nodes_to_add)
            self.session.commit()

        if edges_to_add:
            self.bulk_add(edges_to_add)
            self.session.commit()

        if locations_to_add:
            self.bulk_add(locations_to_add)
            self.session.commit()

    def ensure_default_presets(self):
        existing_codes = {
            row[0] for row in self.session.execute(select(GraphPresetModel.preset_code)).all()
        }

        missing = []
        for preset in DEFAULT_GRAPH_PRESETS:
            if preset["preset_code"] not in existing_codes:
                missing.append(preset)

        if not missing:
            return

        for preset in missing:
            self.session.add(GraphPresetModel(**preset))

        self.session.commit()

    def list_graph_presets(self):
        stmt = (
            select(GraphPresetModel)
            .where(GraphPresetModel.is_active.is_(True))
            .order_by(GraphPresetModel.name.asc())
        )
        presets = self.session.execute(stmt).scalars().all()

        data = []
        for preset in presets:
            data.append({
                "code": preset.preset_code,
                "name": preset.name,
                "lat": float(preset.latitude),
                "lon": float(preset.longitude),
                "is_active": bool(preset.is_active),
                "has_snapshot": preset.snapshot_json is not None,
            })

        return data

    def get_graph_preset_by_code(self, preset_code):
        stmt = select(GraphPresetModel).where(
            GraphPresetModel.preset_code == preset_code,
            GraphPresetModel.is_active.is_(True),
        )
        preset = self.session.execute(stmt).scalars().first()
        if not preset:
            return None

        return {
            "code": preset.preset_code,
            "name": preset.name,
            "lat": float(preset.latitude),
            "lon": float(preset.longitude),
            "is_active": bool(preset.is_active),
            "has_snapshot": preset.snapshot_json is not None,
            "snapshot": preset.snapshot_json,
        }

    def get_graph_preset_snapshot(self, preset_code):
        stmt = select(GraphPresetModel).where(
            GraphPresetModel.preset_code == preset_code,
            GraphPresetModel.is_active.is_(True),
        )
        preset = self.session.execute(stmt).scalars().first()
        if not preset:
            return None
        return preset.snapshot_json

    def upsert_graph_preset_snapshot(self, preset_code, snapshot_json):
        stmt = select(GraphPresetModel).where(GraphPresetModel.preset_code == preset_code)
        preset = self.session.execute(stmt).scalars().first()
        if not preset:
            return False

        preset.snapshot_json = snapshot_json
        self.session.commit()
        return True

    def _linestring_to_wkt(self, coordinates):
        parts = []
        for item in coordinates:
            if not isinstance(item, (list, tuple)) or len(item) < 2:
                continue
            parts.append(f"{float(item[0])} {float(item[1])}")
        return f"LINESTRING ({', '.join(parts)})"