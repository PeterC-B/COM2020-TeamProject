#from app.domain.routing.algorithms.yen_algorithm import yens
#from app.domain.routing.algorithms.dijkstra_algorithm import dijkstra
import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd
from app.extensions import db
from app.models.edges_model import EdgesModel
from app.models.location_model import LocationModel
from app.models.nodes_model import NodesModel
from shapely import wkt
from shapely.geometry import Point
from shapely.ops import unary_union
from sqlalchemy import func


def get_dict_of_edges(graph : nx.MultiDiGraph):
    _, edges_gdf = ox.graph_to_gdfs(graph)
    edges_gdf = edges_gdf.reset_index()

    all_edges = {}

    for _, row in edges_gdf.iterrows():
        u = row["u"]
        v = row["v"]
        length = row["length"]

        all_edges.setdefault(u, {})

        if v not in all_edges[u] or length < all_edges[u][v]:
            all_edges[u][v] = length

    return all_edges

def nodes_csv_to_gdf(csv_path: str = "server/data/processed/nodes_table.csv", crs="EPSG:4326") -> gpd.GeoDataFrame:
    df = pd.read_csv(csv_path)

    geometry = [
        Point(xy) for xy in zip(df["x"], df["y"])
    ]

    node_id_col = "node_id"

    gdf = gpd.GeoDataFrame(
        df,
        geometry=geometry,
        crs=crs
    )

    gdf = gdf.set_index(node_id_col)

    return gdf

def edges_csv_to_gdf(
    edges_csv: str = "server/data/processed/edges_table.csv",
    geom_csv: str = "server/data/processed/edges_geometry.csv",
    crs="EPSG:4326"
) -> gpd.GeoDataFrame:

    edges_df = pd.read_csv(edges_csv)
    geom_df = pd.read_csv(geom_csv)

    geom_df["geometry"] = geom_df["geometry"].apply(wkt.loads)

    gdf = edges_df.merge(
        geom_df,
        left_on=["from_node", "to_node", "key"],
        right_on=["u", "v", "key"],
        how="inner"
    )

    gdf = gdf.drop(columns=["from_node", "to_node", "edge_id"])

    gdf = gpd.GeoDataFrame(gdf, geometry="geometry", crs=crs)
    gdf = gdf.set_index(["u","v","key"])

    return gdf

def edges_in_path(path_of_nodes : list[int], edges_gdf : gpd.GeoDataFrame):
    pairs = list(zip(path_of_nodes[:-1], path_of_nodes[1:]))
    route_edges = edges_gdf[
        edges_gdf.apply(
            lambda r: (r["from_node"], r["to_node"]) in pairs,
            axis=1
        )
    ]
    return route_edges


def path_to_linestring(route_edges: gpd.GeoDataFrame):
    return unary_union(route_edges.geometry)

def path_to_geojson(route_edges: gpd.GeoDataFrame) -> dict:
    geometry = unary_union(route_edges.geometry)

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": geometry.__geo_interface__,
                "properties": {}
            }
        ]
    }

def get_number_of_feature(feature : str) -> int:
    features = (
        db.session
        .query(NodesModel)
        .filter(NodesModel.feature == feature)
        .count()
    )
    return features

def get_total_distance(edge_list : list[int]) -> float:
    distance = (
        db.session
        .query(func.sum(EdgesModel.length))
        .filter(EdgesModel.edge_id.in_(edge_list))
        .scalar()
    )
    if distance is None:
        return 0.0
    return distance

def get_start_and_end_node(edge_list : list[int]) -> tuple[int, int]:
    start_location = (
        db.session
        .query(LocationModel.name, LocationModel.type)
        .filter(LocationModel.node_id == edge_list[0])
        .scalar()
    )

    end_location = (
        db.session
        .query(LocationModel.name, LocationModel.type)
        .filter(LocationModel.node_id == edge_list[len(edge_list)-1])
        .scalar()
    )

    return start_location, end_location

def get_travel_time(edge_list : list[int]) -> float:
    time = (
        db.session
        .query(func.sum(EdgesModel.travel_time))
        .filter(EdgesModel.edge_id.in_(edge_list))
        .scalar()
    )
    if time is None:
        return 0.0
    return time

if __name__ == "__main__":
    print(edges_csv_to_gdf())