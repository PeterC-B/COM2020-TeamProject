from json import dump
from pathlib import Path

import server.app.api.helpers.algorithm_helper as help_algos
import osmnx as ox
from server.app.api.responses import ok
from server.app.domain.errors import ValidationError
from server.app.domain.routing.algorithms.yen_algorithm import yens
from server.app.extensions import db
from server.app.data.convert import (build_edges_geojson, build_nodes_geojson,
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

JSON_PATH = "server/app/api/helpers/edge_list.json"

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
    from server.app.models.enums.HIGHWAY_FEATURES import HighwayFeatures
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
    from server.app.models.enums.HIGHWAY_FEATURES import HighwayFeatures
    feature_dict = {}
    for feature in HighwayFeatures:
        feature_name = f"{feature.value}s" if feature.value[len(feature.value) - 1] != "s" else feature.value
        feature_dict[feature_name] = help_algos.get_number_of_feature(feature)

    route_info = {
        "start_and_end" : start_and_end,
        "stats" : stats,
        "traffic_feature_count" : feature_dict
    }

    with open("server/app/api/helpers/route_info.json", 'w') as f:
        dump({"route_data":route_info}, f, indent=4)

# Testing
def edges_to_json(edge_list : list):
    import json
    with open(JSON_PATH, 'w') as f:
        json.dump(edge_list, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    edge_list = [104804, 282237615, 19875363, 5906108608, 19875366, 104837, 5906030287, 262442708, 104838, 287226483, 3332266263, 287226495, 3696173720, 9464338656, 644926923, 5823455892, 3329881929, 6937982874, 1280853173, 1382252976, 247834407, 242756955, 17406787, 104859, 365559371, 13288882110]
    with app.app_context():
        db.create_all()
        get_route_breakdown_main(edge_list)
        get_route_breakdown_main(edge_list)
