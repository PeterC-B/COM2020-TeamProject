from server.app.domain.routing.algorithms.yen_algorithm import yens
from server.app.api.helpers.algorithm_helper import get_dict_of_edges, edges_csv_to_gdf, nodes_csv_to_gdf, edges_in_path, path_to_geojson
import networkx as nx
import osmnx as ox
from pathlib import Path

from flask import Blueprint, request, jsonify


from client.public.convert import (
    load_edge_geometries,
    build_nodes_geojson,
    build_edges_geojson,
)

from server.app.domain.scoring.cost_functions import HS_ATTRIBUTES, explain_cost
from server.app.domain.scoring.weight_utils import DEFAULT_WEIGHTS, validate_weights
from server.app.api.utils.error_utils import (
    missing_json_body,
    missing_field,
    invalid_weights,
)

route_bp = Blueprint("route", __name__)

DATA_PATH = Path("client/public")
NODES_CSV = DATA_PATH / "nodes_table.csv"
EDGES_CSV = DATA_PATH / "edges_table.csv"
GEOM_CSV = DATA_PATH / "edges_geometry.csv"

edge_geometries = load_edge_geometries(GEOM_CSV)
nodes_geojson = build_nodes_geojson(NODES_CSV)
edges_geojson = build_edges_geojson(EDGES_CSV, edge_geometries)

JSON_PATH = "server/app/api/helpers/edge_list.json"

NODES_GDF = nodes_csv_to_gdf()
EDGES_GDF = edges_csv_to_gdf()

GRAPH = ox.graph_from_gdfs(NODES_GDF, EDGES_GDF)

@route_bp.route("/routing", methods=["GET"])
def run_route_algorithm():
    start_node = request.args.get("start", type=int)
    end_node = request.args.get("end", type=int)

    if start_node is None or end_node is None:
        return jsonify({"error": "Start and end nodes required"}), 400

    edge_list = get_dict_of_edges(GRAPH)
    if start_node not in GRAPH or end_node not in GRAPH:
        return jsonify({"error" : "Invalid start or end node"}), 400
    
    shortest_paths = yens(edge_list, start_node, end_node)
    route_geojson = {}
    order = ["shortestPath", "secondPath", "thirdPath"]
    
    for name, path in zip(order, shortest_paths):
        route_edges = edges_in_path(path, EDGES_GDF)
        route_geojson[name] = path_to_geojson(route_edges)

    return jsonify(route_geojson)
    

def edges_to_json(edge_list : list):
    import json
    with open(JSON_PATH, 'w') as f:
        json.dump(edge_list, f, ensure_ascii=False, indent=4)