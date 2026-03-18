import time

import geopandas as gpd
import osmnx as ox
from scripts.visualisation.visualisation_utils import add_lighting_tag, add_surface_tag

from app.domain.errors import InfrastructureError, NotFoundError
from app.domain.indicators.attribute_extraction import attach_edge_indicators
from app.domain.scoring.weight_utils import add_pub_distance, normalize_pub_distance
from app.models.edges_model import EdgesModel
from app.models.enums.LOCATION_TYPE import LocationType
from app.models.location_model import LocationModel
from app.models.nodes_model import NodesModel

AMENITY_IMPORTANCE = {
    "hospital": 10,
    "police": 9,
    "fire_station": 9,
    "pharmacy": 9,

    "bus_station": 8,
    "taxi": 8,
    "parking": 7,

    "pub": 8,
    "bar": 8,
    "restaurant": 8,
    "cafe": 7,

    "bank": 7,
    "atm": 6,
    "post_office": 7,
    "marketplace": 6,

    "cinema": 6,
    "theatre": 6,
    "nightclub": 6,
    "casino": 6,
}
NO_DATA_MESSAGE = "No data available for this area. Please select a different area."
SEARCH_RADIUS_METERS = 1000

class FetchDataForCoordinates:
    def __init__(self, uow, graph_data_repo=None):
        self.uow = uow
        self.graph_data_repo = graph_data_repo

    def execute(self, coords: tuple[float, float]):
        # Added counter in for debugging purposes and helping us keep track of whether it is hanging or it is just taking a while to finish
        
        started_at = time.perf_counter()
        stage_at = started_at

        def mark(stage_name: str):
            nonlocal stage_at
            now = time.perf_counter()
            print(
                f"[FetchDataForCoordinates] {stage_name}: "
                f"+{(now - stage_at):.2f}s (total {(now - started_at):.2f}s)"
            )
            stage_at = now

        print(f"[FetchDataForCoordinates] start coords={coords}")

        graph = ox.graph_from_point(
            coords,
            dist=SEARCH_RADIUS_METERS,
            network_type="walk",
            dist_type="bbox",
        )
        try:
            graph = ox.add_edge_speeds(graph, fallback=4.5)
        except Exception:
            for _, _, _, data in graph.edges(keys=True, data=True):
                data["speed_kph"] = data.get("speed_kph", 4.5)

        graph = ox.add_edge_travel_times(graph)

        try:
            graph = add_lighting_tag(graph, coords, SEARCH_RADIUS_METERS)
        except Exception:
            raise NotFoundError(message=NO_DATA_MESSAGE)

        try:
            graph = add_surface_tag(graph, coords, SEARCH_RADIUS_METERS)
        except Exception:
            raise NotFoundError(message=NO_DATA_MESSAGE)
        mark("graph download + enrichment")

        nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)

        try:
            polygon = nodes_gdf.unary_union.convex_hull
            amenities = ox.features_from_polygon(
                polygon,
                tags={"amenity": True}
            )
            amenities = amenities[amenities.geometry.notnull()].copy()
            # Compute centroids in a projected CRS to avoid geographic-centroid inaccuracies.
            amenities_projected = amenities.to_crs(epsg=27700)
            amenities_projected["geometry"] = amenities_projected.geometry.centroid
            amenities = amenities_projected.to_crs(epsg=4326)
            amenities["importance"] = amenities["amenity"].map(AMENITY_IMPORTANCE).fillna(1)
            amenities = amenities.sort_values("importance", ascending=False)
        except Exception:
            raise NotFoundError(message=NO_DATA_MESSAGE)
        mark("amenity fetch + ranking")

        try:
            drink_places = ox.features_from_point(
                coords,
                tags={"amenity": ["bar", "biergarten", "pub", "casino", "nightclub", "gambling"]},
                dist=SEARCH_RADIUS_METERS
            )
            drink_places = drink_places[drink_places.geometry.notnull()].copy()
        except Exception:
            raise NotFoundError(message=NO_DATA_MESSAGE)
        mark("drinking places fetch")

        edges_m = edges_gdf.to_crs(epsg=27700)
        amenities_m = drink_places.to_crs(epsg=27700)

        nearest = gpd.sjoin_nearest(
            edges_m,
            amenities_m,
            how="left",
            distance_col="dist_to_amenity"
        )

        nearest["access_score"] = nearest["dist_to_amenity"].apply(
            lambda d: 0 if d is None or d > 1000 else 10 / (d + 1)
        )

        # sjoin_nearest may emit multiple rows per edge (e.g., tie distances).
        # Collapse to one score per original edge index before assignment.
        edge_scores = nearest.groupby(level=0)["access_score"].max()
        edges_gdf["score_band"] = (
            edge_scores.reindex(edges_gdf.index)
            .fillna(0.0)
            .astype(float)
        )

        edges_gdf = attach_edge_indicators(edges_gdf)
        edges_gdf = add_pub_distance(coords, edges_gdf, SEARCH_RADIUS_METERS)

        edges_gdf["normalised_pub_distance"]= (
            edges_gdf["distance_to_pub"]
            .apply(normalize_pub_distance)
        )
        mark("edge indicators + scoring")

        nodes_df = nodes_gdf.reset_index().rename(columns={"osmid": "node_id"})
        edges_df = edges_gdf.reset_index()
        edges_df["geometry"] = edges_df["geometry"].apply(
            lambda geom: geom.wkt if hasattr(geom, "wkt") else str(geom)
        )

        with self.uow:
            self.graph_data_repo.clear_tables()
            nodes = [NodesModel(
                node_id=row["node_id"],
                x_coordinate=row["x"],
                y_coordinate=row["y"],
                feature=row.get("highway")
            )
            for _, row in nodes_df.iterrows()
            ]
            self.graph_data_repo.bulk_add(nodes)
            self.uow.commit()
            
            edges = [
                EdgesModel(
                    edge_id=i,
                    from_node_id=row["u"],
                    to_node_id=row["v"],
                    key=row["key"],
                    length=row.get("length"),
                    travel_time=row.get("travel_time"),
                    access_score=row.get("score_band"),
                    geometry=row["geometry"],
                    lighting=row["lighting"],
                    greenery=row["greenery"],
                    pollution=row["pollution"],
                    surface_quality=row["surface_quality"],
                    pub_distance=row["normalised_pub_distance"]
                )
                for i, row in edges_df.iterrows()
            ]
            self.graph_data_repo.bulk_add(edges)
            self.uow.commit()
        mark("db write nodes + edges")

        locations_to_add = []

        # Use projected graph + coordinates for accurate nearest-node mapping.
        graph_projected = ox.project_graph(graph, to_crs="EPSG:27700")
        amenities_for_nodes = amenities.to_crs(epsg=27700)
        amenity_x = amenities_for_nodes.geometry.x.values
        amenity_y = amenities_for_nodes.geometry.y.values
        try:
            nearest_nodes = ox.distance.nearest_nodes(
                graph_projected,
                X=amenity_x,
                Y=amenity_y,
            )
        except Exception as exc:
            message = str(exc).lower()
            if isinstance(exc, (ImportError, ModuleNotFoundError)) or any(
                token in message for token in ("scipy", "sklearn", "scikit-learn")
            ):
                raise InfrastructureError(
                    message=(
                        "Nearest-node dependencies are missing. "
                        "Install scipy (and optionally scikit-learn) on the server."
                    )
                )
            raise
        mark("nearest amenity nodes")

        for (_, row), node in zip(amenities.iterrows(), nearest_nodes):
            location = LocationModel(
                name=row.get("name") or row.get("amenity") or "Unnamed Amenity",
                node_id=int(node),
                type=LocationType.GENERAL_AMENITY,
                information=row.get("amenity"),
                in_use=True
            )

            locations_to_add.append(location)

        with self.uow:
            self.graph_data_repo.bulk_add(locations_to_add)
            self.uow.commit()
        mark("db write locations")

        result = {"features": self.graph_data_repo.get_graph_features()}
        mark("build response payload")
        print(f"[FetchDataForCoordinates] done total={(time.perf_counter() - started_at):.2f}s")
        return result