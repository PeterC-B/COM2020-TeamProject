"""
Routing Endpoints:
    - /route/dijkstra
    - /route/astar
    - /route/yens

These endpoints:
    - Parse user input (start, end, weights, k)
    - Validate coordinates and weights
    - Convert coordinates -> nearest graph nodes
    - Call the appropriate routing algorithm
    - Format and return the response
"""
from flask import Blueprint, request, jsonify

# Utilities
from utils.node_utils import get_nearest_node, validate_coordiates
from utils.weight_utils import validate_weights, apply_default_weights
from utils.response_utils import format_route_response, format_error

# Graph + cost
from graph.graph_cache import load_cached_graph
from cost.cost_functions import healthy_cost

# Algorithms
from algorithms.dijkstra_algorithm import dijkstra
from algorithms.astar_algorithm import astar
from algorithms.yen_algorithm import yens

routing_bp = Blueprint("routing", __name__)

@routing_bp.route("/route/dijkstra_algorithm", methods=["POST"])
# Compute a route using Dijkstra's algorithm
def route_dijkstra():
    pass

@routing_bp.route("/route/astar_algorithm", methods=["POST"])
# Compute a route using A* search
def route_astar():
    pass

@routing_bp.route("/route/yens_algorithm", methods=["POST"])
# Compute K shortest routes using Yen's algorithm
def route_yens():
    pass
    