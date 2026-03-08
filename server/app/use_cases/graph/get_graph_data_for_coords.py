import osmnx as ox
import geopandas as gpd
from server.app.domain.routing.graph_cache import save_cached_graph
from server.app.domain.errors import NotFoundError
from server.scripts.visualisation.visualisation_utils import add_lighting_tag, add_surface_tag, add_crime_rating
from server.app.domain.scoring.weight_utils import calculate_weights
from server.app.domain.indicators.attribute_extraction import attach_edge_indicators
import os

class FetchDataForCoordinates:
    def __init__(self, graph_data_repo=None):
        self.graph_data_repo = graph_data_repo

    def execute(self, coords: tuple[float, float]):
        graph = ox.graph_from_point(coords, dist=700, network_type="walk", dist_type="network")
        graph = ox.add_edge_speeds(graph)
        graph = ox.add_edge_travel_times(graph)

        try:
            amenities = ox.features_from_point(coords, tags={"amenity": True}, dist=500)
            amenities = amenities[amenities.geometry.notnull()].copy()
            amenities["geometry"] = amenities.geometry.centroid
        except Exception:
            raise NotFoundError(message="Unable to find amenities")

        sample_size = min(80, len(amenities))
        random_amenities = amenities.sample(n=sample_size, random_state=42)

        for _, row in random_amenities.iterrows():
            x, y = row.geometry.x, row.geometry.y
            nearest_node = ox.distance.nearest_nodes(graph, X=x, Y=y)
            graph.nodes[nearest_node]["amenity"] = row.get("amenity")
            graph.nodes[nearest_node]["amenity_name"] = row.get("name")

        nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)

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

        output_dir = "server/app/data/processed"
        os.makedirs(output_dir, exist_ok=True)

        # Nodes CSV
        nodes_export = nodes_gdf.reset_index().rename(columns={"osmid": "node_id"})
        nodes_export = nodes_export[["node_id", "x", "y", "highway"]]
        nodes_export.to_csv(os.path.join(output_dir, "nodes_table.csv"), index=False)

        # Edges CSV
        edges_export = edges_gdf.reset_index().rename(columns={"u": "from_node", "v": "to_node"})
        edges_export["edge_id"] = edges_export.index
        edges_main = edges_export[["edge_id", "from_node", "to_node", "key", "length", "travel_time"]]
        edges_main.to_csv(os.path.join(output_dir, "edges_table.csv"), index=False)

        # Edges geometry CSV
        edges_geometry = edges_export[["from_node", "to_node", "key", "geometry"]].copy()
        edges_geometry = edges_geometry.rename(columns={
            "from_node": "u",
            "to_node": "v",
        })
        edges_geometry["geometry"] = edges_geometry["geometry"].to_wkt()
        edges_geometry.to_csv(os.path.join(output_dir, "edges_geometry.csv"), index=False)

        save_cached_graph(graph)