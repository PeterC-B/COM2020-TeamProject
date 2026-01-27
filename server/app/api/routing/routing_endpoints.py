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
from app.domain.routing.nearest_node import get_nearest_node
from app.domain.routing.validate_coordinates import validate_coordinates
from app.domain.scoring.weight_utils import validate_weights, apply_default_weights
from app.api.utils.response_utils import format_route_response

# Error utilities
from app.api.utils.error_utils import (
    missing_json_body,
    invalid_coordinates,
    invalid_weights,
    route_not_found,
    routes_not_found,
    graph_not_loaded,
    error_response,
)

# Graph + cost
from app.domain.routing.graph_cache import load_cached_graph
from app.domain.scoring.cost_functions import healthy_cost

# Algorithms
from app.domain.routing.algorithms.dijkstra_algorithm import dijkstra
from app.domain.routing.algorithms.astar_algorithm import astar
from app.domain.routing.algorithms.yen_algorithm import yens


routing_bp = Blueprint("routing", __name__)


# -----------------------------
# Helper: Load graph or return error
# -----------------------------
def load_graph_or_error():
    graph = load_cached_graph()
    if graph is None:
        return None, *graph_not_loaded()
    return graph, None, None


# -----------------------------
# Dijkstra Endpoint
# -----------------------------
@routing_bp.route("/route/dijkstra", methods=["POST"])
def route_dijkstra():
    data = request.get_json()
    if not data:
        return missing_json_body()

    start = data.get("start")
    end = data.get("end")
    weights = data.get("weights")

    if not validate_coordinates(start) or not validate_coordinates(end):
        return invalid_coordinates()

    if weights is None:
        weights = apply_default_weights()
    elif not validate_weights(weights):
        return invalid_weights()

    graph, err, code = load_graph_or_error()
    if err:
        return err, code

    start_node = get_nearest_node(graph, start)
    end_node = get_nearest_node(graph, end)

    def cost_fn(u, v):
        edge_data = graph.get_edge_data(u, v)
        first_key = next(iter(edge_data))
        return healthy_cost(edge_data[first_key], weights)

    path = dijkstra(graph, start_node, end_node, cost_fn)

    if path is None:
        return route_not_found()

    return jsonify(format_route_response(path, graph, weights=weights))


# -----------------------------
# A* Endpoint
# -----------------------------
@routing_bp.route("/route/astar", methods=["POST"])
def route_astar():
    data = request.get_json()
    if not data:
        return missing_json_body()

    start = data.get("start")
    end = data.get("end")
    weights = data.get("weights")

    if not validate_coordinates(start) or not validate_coordinates(end):
        return invalid_coordinates()

    if weights is None:
        weights = apply_default_weights()
    elif not validate_weights(weights):
        return invalid_weights()

    graph, err, code = load_graph_or_error()
    if err:
        return err, code

    start_node = get_nearest_node(graph, start)
    end_node = get_nearest_node(graph, end)

    def cost_fn(u, v):
        edge_data = graph.get_edge_data(u, v)
        first_key = next(iter(edge_data))
        return healthy_cost(edge_data[first_key], weights)

    def heuristic(u, v):
        ux, uy = graph.nodes[u]["x"], graph.nodes[u]["y"]
        vx, vy = graph.nodes[v]["x"], graph.nodes[v]["y"]
        return (ux - vx) ** 2 + (uy - vy) ** 2

    path = astar(graph, start_node, end_node, cost_fn, heuristic)

    if path is None:
        return route_not_found()

    return jsonify(format_route_response(path, graph, weights=weights))


# -----------------------------
# Yen's K-shortest Paths Endpoint
# -----------------------------
@routing_bp.route("/route/yens", methods=["POST"])
def route_yens():
    data = request.get_json()
    if not data:
        return missing_json_body()

    start = data.get("start")
    end = data.get("end")
    k = data.get("k", 3)
    weights = data.get("weights")

    if not validate_coordinates(start) or not validate_coordinates(end):
        return invalid_coordinates()

    if not isinstance(k, int) or k < 1:
        return error_response("Parameter 'k' must be a positive integer")

    if weights is None:
        weights = apply_default_weights()
    elif not validate_weights(weights):
        return invalid_weights()

    graph, err, code = load_graph_or_error()
    if err:
        return err, code

    start_node = get_nearest_node(graph, start)
    end_node = get_nearest_node(graph, end)

    def cost_fn(u, v):
        edge_data = graph.get_edge_data(u, v)
        first_key = next(iter(edge_data))
        return healthy_cost(edge_data[first_key], weights)

    paths = yens(graph, start_node, end_node, k, cost_fn)

    if not paths:
        return routes_not_found()

    return jsonify({
        "routes": [
            format_route_response(path, graph, weights=weights)
            for path in paths
        ]
    })
