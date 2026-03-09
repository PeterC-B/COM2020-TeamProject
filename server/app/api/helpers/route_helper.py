from json import dump
from pathlib import Path

import app.api.helpers.algorithm_helper as help_algos
import osmnx as ox
from app.api.responses import ok
from app.domain.errors import ValidationError
from app.domain.routing.algorithms.yen_algorithm import yens
from app.extensions import db
from app.data.convert import (build_edges_geojson, build_nodes_geojson,
                                   load_edge_geometries)
from flask import Blueprint, request

route_bp = Blueprint("route", __name__)

DATA_PATH = Path("client/public")
NODES_CSV = DATA_PATH / "nodes_table.csv"
EDGES_CSV = DATA_PATH / "edges_table.csv"
GEOM_CSV = DATA_PATH / "edges_geometry.csv"

edge_geometries = load_edge_geometries(GEOM_CSV)
nodes_geojson = build_nodes_geojson(NODES_CSV)
edges_geojson = build_edges_geojson(EDGES_CSV, edge_geometries)

JSON_PATH = "app/api/helpers/edge_list.json"

NODES_GDF = help_algos.nodes_csv_to_gdf()
EDGES_GDF = help_algos.edges_csv_to_gdf()

GRAPH = ox.graph_from_gdfs(NODES_GDF, EDGES_GDF)
  
@route_bp.route("/routing", methods=["GET"])
def run_route_algorithm():
    start_node = request.args.get("start", type=int)
    end_node = request.args.get("end", type=int)

    if start_node is None or end_node is None:
        raise ValidationError(
            message="Start and end nodes required",
            details={"required_fields": ["start", "end"]},
        )

    edge_list = help_algos.get_dict_of_edges(GRAPH)

    if start_node not in GRAPH or end_node not in GRAPH:
        raise ValidationError(
            message="Invalid start or end node",
            details={"start": start_node, "end": end_node},
        )
    
    shortest_paths = yens(edge_list, start_node, end_node)
    route_geojson = {}
    order = ["shortestPath", "secondPath", "thirdPath"]
    
    for name, path in zip(order, shortest_paths):
        route_edges = help_algos.edges_in_path(path, EDGES_GDF)
        route_geojson[name] = help_algos.path_to_geojson(route_edges)

    return ok(data=route_geojson)
    
@route_bp.route("/route_breakdown", methods=["GET"])
def get_route_breakdown():
    edge_list = request.args.get("edge_list", type=list)
    # Get start / end node names
    start_location, end_location = help_algos.get_start_and_end_node(edge_list)

    start_and_end = {
        "start_location" : start_location,
        "end_location" : end_location
    }

    # Get count of edges / roads
    number_of_edges = len(edge_list)

    # Get total distance
    total_distance = help_algos.get_total_distance(edge_list)

    # Work out total time
    total_time = help_algos.get_travel_time(edge_list)
    
    stats = {
        "edge_count" : number_of_edges,
        "distance" : total_distance,
        "time" : total_time
    }

    # Get count of crossings, traffic lights, turning circles
    from app.models.enums.HIGHWAY_FEATURES import HighwayFeatures
    feature_dict = {}
    for feature in HighwayFeatures:
        feature_name = f"{feature.value}s" if feature.value[len(feature.value) - 1] != "s" else feature.value
        feature_dict[feature_name] = help_algos.get_number_of_feature(feature)

    route_info = {
        "start_and_end" : start_and_end,
        "stats" : stats,
        "traffic_feature_count" : feature_dict
    }

    return ok(data={"route_data": route_info})


def get_route_breakdown_main(edge_list):
    # Get start / end node names
    start_location, end_location = help_algos.get_start_and_end_node(edge_list)

    start_and_end = {
        "start_location" : start_location,
        "end_location" : end_location
    }

    # Get count of edges / roads
    number_of_edges = len(edge_list)

    # Get total distance
    total_distance = help_algos.get_total_distance(edge_list)

    # Work out total time
    total_time = help_algos.get_travel_time(edge_list)
    
    stats = {
        "edge_count" : number_of_edges,
        "distance" : total_distance,
        "time" : total_time
    }

    # Get count of crossings, traffic lights, turning circles
    from app.models.enums.HIGHWAY_FEATURES import HighwayFeatures
    feature_dict = {}
    for feature in HighwayFeatures:
        feature_name = f"{feature.value}s" if feature.value[len(feature.value) - 1] != "s" else feature.value
        feature_dict[feature_name] = help_algos.get_number_of_feature(feature)

    route_info = {
        "start_and_end" : start_and_end,
        "stats" : stats,
        "traffic_feature_count" : feature_dict
    }

    with open("app/api/helpers/route_info.json", 'w') as f:
        dump({"route_data":route_info}, f, indent=4)

# Testing
def edges_to_json(edge_list : list):
    import json
    with open(JSON_PATH, 'w') as f:
        json.dump(edge_list, f, ensure_ascii=False, indent=4)