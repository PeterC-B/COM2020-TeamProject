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

def load_graph_or_error():
    graph = load_cached_graph
    if graph is None:
        return None, format_error("No cached graph found. Build the graph first")
    return graph, None

@routing_bp.route("/route/dijkstra_algorithm", methods=["POST"])
def route_dijkstra():
    data = request.get_json()

    if not data:
        return format_error("Missing JSON body")
    
    start = data.get("start")
    end = data.get("end")
    weights = data.get("weights")

    # Validate coordinates
    if not validate_coordiates(start) or not validate_coordiates(end):
        return format_error("Invalid coordiantes provided")
    
    # Validate or apply default weights
    if weights is None:
        weights = apply_default_weights()
    elif not validate_weights(weights):
        return format_error("Invalid weight configuration")
    
    # Load graph
    graph, err = load_graph_or_error()
    if err:
        return err
    
    # Convert coordinates -> nearest nodes
    start_node = get_nearest_node(start, graph)
    end_node = get_nearest_node(end, graph)

    # Run Dijkstra
    path = dijkstra(graph, start_node, end_node, lambda u, v: healthy_cost(graph[u][v], weights))

    if path is None:
        return format_error("No route found")
    
    return jsonify(format_route_response(path, graph))

@routing_bp.route("/route/astar_algorithm", methods=["POST"])
# Compute a route using A* search
def route_astar():
    data = request.get_json()

    if not data:
        return format_error("Missing JSON body")
    
    start = data.get("start")
    end = data.get("end")
    weights = data.get("weights")

    # Validate coordinates
    if not validate_coordiates(start) or not validate_coordiates(end):
        return format_error("Invalid coordiantes provided")
    
    # Validate or apply default weights
    if weights is None:
        weights = apply_default_weights()
    elif not validate_weights(weights):
        return format_error("Invalid weight configuration")
    
    # Load graph
    graph, err = load_graph_or_error()
    if err:
        return err
    
    # Convert coordinates -> nearest nodes
    start_node = get_nearest_node(start, graph)
    end_node = get_nearest_node(end, graph)

    def heuristic(u, v):
        return graph[u][v]["distance"]
    
    path = astar(graph, start_node, end_node,
                 lambda u, v: healthy_cost(graph[u][v], weights),
                 heuristic)
    
    if path is None:
        return format_error("No route found")
    
    return jsonify(format_route_response(path,graph))

@routing_bp.route("/route/yens_algorithm", methods=["POST"])
# Compute K shortest routes using Yen's algorithm
def route_yens():
    data = request.get_json()

    if not data:
        return format_error("Missing JSON body")
    
    start = data.get("start")
    end = data.get("end")
    k = data.get("k", 3)
    weights = data.get("weights")

    if not validate_coordiates(start) or not validate_coordiates(end):
        return format_error("Invalid coordiantes provided")
    
    if not isinstance(k, int) or k < 1:
        return format_error("Parameter 'k' must be a positive integer")
    
    if weights is None:
        weights = apply_default_weights()
    elif not validate_weights(weights):
        return format_error("Invalid weight configuration")
    
    graph, err = load_graph_or_error()
    if err:
        return err
    
    start_node = get_nearest_node(start, graph)
    end_node = get_nearest_node(end, graph)

    cost_fn = lambda u, v: healthy_cost(graph[u][v], weights)

    paths = yens(graph, start_node, end_node, k, cost_fn)

    if not paths:
        return format_error("No routes found")
    
    return jsonify({
        "routes": [format_route_response(path, graph) for path in paths]
    })