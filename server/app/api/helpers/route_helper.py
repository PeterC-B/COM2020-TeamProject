from server.app.domain.routing.algorithms.yen_algorithm import yens
from server.app.api.helpers.algorithm_helper import get_dict_of_edges
import networkx as nx

from flask import Blueprint, request, jsonify

from server.app.domain.scoring.cost_functions import HS_ATTRIBUTES, explain_cost
from server.app.domain.scoring.weight_utils import DEFAULT_WEIGHTS, validate_weights
from server.app.api.utils.error_utils import (
    missing_json_body,
    missing_field,
    invalid_weights,
)

route_bp = Blueprint("route", __name__)

JSON_PATH = "server/app/api/helpers/edge_list.json"

@route_bp.route("/routing", methods=["GET"])
def run_route_algorithm(graph : nx.MultiDiGraph, start_node : int, end_node : int, route_algorithm : function = yens):
    edge_list = get_dict_of_edges(graph)
    shortestPaths = route_algorithm(edge_list, start_node, end_node)
    paths = {}
    order = ["shortestPath", "secondPath", "thirdPath"]
    for path, name in zip(shortestPaths, order):
        paths[name] = path
    return jsonify({"paths" : paths})
    

def edges_to_json(edge_list : list):
    import json
    with open(JSON_PATH, 'w') as f:
        json.dump(edge_list, f, ensure_ascii=False, indent=4)
    return json.dump(edge_list, f, ensure_ascii=False, indent=4)