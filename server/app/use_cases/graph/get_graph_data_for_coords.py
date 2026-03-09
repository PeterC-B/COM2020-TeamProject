import osmnx as ox
import geopandas as gpd
from app.domain.routing.graph_cache import save_cached_graph
from app.domain.indicators.attribute_extraction import attach_edge_indicators, compute_amenity_proximity
from scripts.visualisation.visualisation_utils import add_lighting_tag, add_surface_tag
from app.domain.scoring.weight_utils import add_pub_distance, normalize_pub_distance
from app.domain.errors import NotFoundError
from app.models.nodes_model import NodesModel
from app.models.edges_model import EdgesModel
from app.models.location_model import LocationModel
from app.models.enums.LOCATION_TYPE import LocationType
import numpy as np
import pandas as pd

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

class FetchDataForCoordinates:
    def __init__(self, uow, graph_data_repo=None):
        self.uow = uow
        self.graph_data_repo = graph_data_repo

    def execute(self, coords: tuple[float, float]):
        graph = ox.graph_from_point(coords, dist=500, network_type="walk", dist_type="bbox")
        graph = ox.add_edge_speeds(graph)
        graph = ox.add_edge_travel_times(graph)
        graph = add_lighting_tag(graph, coords, 500)
        graph = add_surface_tag(graph, coords, 500)

        nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)
        
        try:
            polygon = nodes_gdf.unary_union.convex_hull
            amenities = ox.features_from_polygon(
                polygon,
                tags={"amenity": True}
            )
            amenities = amenities[amenities.geometry.notnull()].copy()
            amenities["geometry"] = amenities.geometry.centroid
            amenities["importance"] = amenities["amenity"].map(AMENITY_IMPORTANCE).fillna(1)
            amenities = amenities.sort_values("importance", ascending=False)
        except Exception:
            raise NotFoundError(message="Unable to find amenities")

        try:
            drink_places = ox.features_from_point(
                coords,
                tags={"amenity": ["bar", "biergarten", "pub", "casino", "nightclub", "gambling"]},
                dist=450
            )
            drink_places = drink_places[drink_places.geometry.notnull()].copy()
        except Exception:
            raise NotFoundError(message="Unable to find drinking places")

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

        edges_gdf["score_band"] = nearest["access_score"].values  

        edges_gdf = attach_edge_indicators(edges_gdf)
        edges_gdf = add_pub_distance(coords, edges_gdf, 500)
        edges_gdf["normalised_pub_distance"]= (
            edges_gdf["distance_to_pub"]
            .apply(normalize_pub_distance)
        )

        nodes_df = nodes_gdf.reset_index().rename(columns={"osmid": "node_id"})
        edges_df = edges_gdf.reset_index()
        edges_df["geometry"] = edges_df["geometry"].to_wkt()

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
        
        locations_to_add = []

        xs = amenities.geometry.x.values
        ys = amenities.geometry.y.values

        nearest_nodes = ox.distance.nearest_nodes(graph, X=xs, Y=ys)

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


        #save_cached_graph(graph)