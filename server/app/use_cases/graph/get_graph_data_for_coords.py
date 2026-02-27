import osmnx as ox
import os
import geopandas as gpd
from server.app.domain.routing.graph_cache import save_cached_graph

class FetchDataForCoordinates:
    def __init__(self, graph_data_repo):
        self.graph_data_repo = graph_data_repo

    def execute(self, coords : tuple[float, float]):
        graph = ox.graph_from_point(coords, 500, network_type="walk", dist_type="bbox")
        graph = ox.add_edge_speeds(graph)
        graph = ox.add_edge_travel_times(graph)

        tags = {"amenity" : True}
        amenities = ox.features_from_point(coords, tags, 500)
        amenities = amenities[amenities.geometry.notnull()].copy()
        amenities["geometry"] = amenities.geometry.centroid

        sample_size = min(80, len(amenities))
        random_amenities = amenities.sample(n=sample_size, random_state=42)

        for idx, row in random_amenities.iterrows():
            x = row.geometry.x
            y = row.geometry.y

            nearest_node = ox.distance.nearest_nodes(graph, x, y)

            graph.nodes[nearest_node]["amenity"] = row.get("amenity")
            graph.nodes[nearest_node]["amenity_name"] = row.get("name")

        output_dir = "server/app/data/processed"

        nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)

        nodes_export = nodes_gdf.reset_index()

        nodes_export = nodes_export.rename(columns={
            "osmid": "node_id"
        })

        nodes_export = nodes_export[[
            "node_id", "x", "y", "highway"
        ]]

        nodes_export.to_csv(
            os.path.join(output_dir, "nodes_table.csv"),
            index=False
        )

        drink_places = ox.features_from_point(
            coords,
            tags={"amenity":[
                    "bar", "biergarten", "pub", "casino", "nightclub", "gambling"
                ]},
            dist=450,
        )

        edges_m = edges_gdf.to_crs(epsg=27700)
        amenities_m = drink_places.to_crs(epsg=27700)

        nearest = gpd.sjoin_nearest(
            edges_m,
            amenities_m,
            how="left",
            distance_col="dist_to_amenity",
        )

        def distance_score(d):
            if d is None or d > 1000:
                return 0
            return 1 / (d+1)
        
        nearest["access_score"] = nearest["dist_to_amenity"].apply(distance_score)
        edges_gdf["access_score"] = nearest["access_score"].values

        edges_export = edges_gdf.reset_index()

        edges_export_renamed = edges_export.rename(columns={
            "u": "from_node",
            "v": "to_node"
        })

        edges_export_renamed["edge_id"] = edges_export_renamed.index

        edges_main = edges_export_renamed[[
            "edge_id",
            "from_node",
            "to_node",
            "key",
            "length",
            "travel_time",
            "access_score",
        ]]

        edges_main.to_csv(
            os.path.join(output_dir, "edges_table.csv"),
            index=False
        )

        edges_geometry = edges_export[[
            "u", "v", "key",
            "geometry"
        ]].copy()

        # Convert geometry to WKT for CSV storage
        edges_geometry["geometry"] = edges_geometry["geometry"].to_wkt()

        edges_geometry.to_csv(
            os.path.join(output_dir, "edges_geometry.csv"),
            index=False
        )

        save_cached_graph(graph)