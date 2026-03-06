import osmnx as ox
import geopandas as gpd
from server.app.domain.routing.graph_cache import save_cached_graph
from server.app.domain.indicators.attribute_extraction import attach_edge_indicators
from server.scripts.visualisation.visualisation_utils import add_lighting_tag, add_surface_tag
from server.app.domain.errors import NotFoundError
from server.app.models.nodes_model import NodesModel
from server.app.models.edges_model import EdgesModel

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

        edges_gdf = attach_edge_indicators(edges_gdf)

        nodes_df = nodes_gdf.reset_index().rename(columns={"osmid": "node_id"})
        edges_df = edges_gdf.reset_index()
        edges_df["geometry"] = edges_df["geometry"].to_wkt()

        with self.uow:
            print("Clearing tables")
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
            print("Adding nodes")
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
                )
                for i, row in edges_df.iterrows()
            ]
            self.graph_data_repo.bulk_add(edges)
            print("Adding edges")
            self.uow.commit()

        #save_cached_graph(graph)