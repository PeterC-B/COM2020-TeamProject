import copy
import heapq

import networkx as nx

from app.api.utils.response_utils import (compare_routes,
                                                 format_route_response)
from app.domain.routing.algorithms.dijkstra_algorithm import dijkstra
from app.domain.routing.graph_cache import load_cached_graph
from app.domain.routing.nearest_node import get_nearest_node
from app.domain.scoring.cost_functions import healthy_cost
from app.domain.scoring.weight_utils import (apply_default_weights,
                                                    validate_weights)


def parse_coordinates(coords):
    """Convert coordinate input to a (lat, lon) float tuple."""
    if isinstance(coords, dict):
        coords = (coords["lat"], coords["lon"])
    elif isinstance(coords, str):
        lat_str, lon_str = coords.split(",", 1)
        coords = (lat_str.strip(), lon_str.strip())

    lat, lon = coords
    return float(lat), float(lon)


def build_weighted_adjacency(graph: nx.MultiDiGraph, weights):
    """
    Convert a MultiDiGraph into a weighted adjacency map
    If parallel edges exist, only the lowest-cost edge is kept in the adjacency representation for Yen's algorithm
    """
    weighted_graph = {}

    for from_node, to_node, _edge_key, edge_data in graph.edges(keys=True, data=True):
        edge_cost = healthy_cost(edge_data, weights)

        if from_node not in weighted_graph:
            weighted_graph[from_node] = {}

        current = weighted_graph[from_node].get(to_node)
        if current is None or edge_cost < current:
            weighted_graph[from_node][to_node] = edge_cost

    return weighted_graph


def compute_path_length(graph, path):
    """Compute total weighted length for a node path in adjacency-dict form."""
    total = 0
    for from_node, to_node in zip(path, path[1:]):
        total += graph[from_node][to_node]
    return total


def yens(graph, source, target, k_paths=3, trace=False):
    """Yen's K-shortest loopless paths on adjacency dict {node: {neighbor: weight}}."""
    original_graph = copy.deepcopy(graph)

    def log(msg):
        if trace:
            print(msg)

    log(f"[START] Yen's Algorithm from {source} to {target}, K = {k_paths}")

    init_dist, init_path = dijkstra(graph, source, target, trace=trace)
    if not init_path:
        log("[FAIL] No initial shortest path found")
        return []

    shortest_paths = [init_path]
    candidate_paths = []

    log(f"[P1] First shortest path: {init_path}")

    for path_index in range(1, k_paths):
        log(f"\n[ITERATION] path_index = {path_index}")
        prev_path = shortest_paths[path_index - 1]

        for spur_index in range(len(prev_path) - 1):
            spur_node = prev_path[spur_index]
            root_path = prev_path[: spur_index + 1]

            log(f"\n[SPUR] spur_index = {spur_index}, spur_node = {spur_node}, root_path = {root_path}")

            removed_edges = []
            removed_nodes = set()

            for existing_path in shortest_paths:
                if len(existing_path) > spur_index and existing_path[: spur_index + 1] == root_path:
                    from_node = existing_path[spur_index]
                    to_node = existing_path[spur_index + 1]
                    if to_node in graph.get(from_node, {}):
                        log(f"  [REMOVE EDGE] {from_node} -> {to_node}")
                        removed_edges.append((from_node, to_node, graph[from_node][to_node]))
                        del graph[from_node][to_node]

            for root_node in root_path[:-1]:
                if root_node in graph:
                    log(f"  [REMOVE NODE] {root_node}")
                    removed_nodes.add(root_node)
                    for neighbor, weight in list(graph[root_node].items()):
                        removed_edges.append((root_node, neighbor, weight))
                    del graph[root_node]

            spur_dist, spur_path = dijkstra(graph, spur_node, target, trace=trace)

            if spur_path:
                total_path = root_path[:-1] + spur_path
                total_dist = compute_path_length(original_graph, total_path)
                log(f"  [CANDIDATE] path = {total_path}, distance = {total_dist}")
                heapq.heappush(candidate_paths, (total_dist, total_path))
            else:
                log("  [NO SPUR PATH]")

            for from_node, to_node, weight in removed_edges:
                if from_node not in graph:
                    graph[from_node] = {}
                graph[from_node][to_node] = weight

            for node in removed_nodes:
                if node not in graph:
                    graph[node] = {}

        if not candidate_paths:
            log("[END] No more candidate paths")
            break

        next_dist, next_path = heapq.heappop(candidate_paths)
        log(f"[P{path_index + 1}] Next shortest path: {next_path}")
        shortest_paths.append(next_path)

    return shortest_paths


def yens_from_multidigraph(graph: nx.MultiDiGraph, source, target, weights, k_paths=3, trace=False):
    """Run Yen's algorithm on a MultiDiGraph using healthy-street weighted edges"""
    weighted_graph = build_weighted_adjacency(graph, weights)
    return yens(weighted_graph, source, target, k_paths=k_paths, trace=trace)


def process_yens_routing_request(data, graph=None):
    """
    Single function to handle the flow of the routing request
    Returns (payload_dict, status_code)
    """
    if not data:
        return {"error": "Missing JSON body"}, 400

    start = data.get("start")
    end = data.get("end")
    raw_weights = data.get("weights")
    k = data.get("k", 3)

    if start is None:
        return {"error": "Missing required field: 'start'"}, 400
    if end is None:
        return {"error": "Missing required field: 'end'"}, 400

    if not isinstance(k, int) or k < 1:
        return {"error": "Parameter 'k' must be a positive integer"}, 400

    if raw_weights is None:
        weights = apply_default_weights()
    elif not validate_weights(raw_weights):
        return {"error": "Invalid weight configuration"}, 400
    else:
        weights = apply_default_weights(raw_weights)

    graph = graph if graph is not None else load_cached_graph()
    if graph is None:
        return {"error": "No cached graph found. Build the graph first."}, 500

    try:
        start_coords = parse_coordinates(start)
        end_coords = parse_coordinates(end)
        start_node = get_nearest_node(graph, start_coords)
        end_node = get_nearest_node(graph, end_coords)
    except (TypeError, ValueError, KeyError):
        return {"error": "Invalid coordinates provided"}, 400

    paths = yens_from_multidigraph(
        graph,
        start_node,
        end_node,
        weights=weights,
        k_paths=k,
        trace=False,
    )

    if not paths:
        return {"error": "No route  s found"}, 404

    routes = [
        format_route_response(
            path,
            graph,
            weights=weights,
            metadata={"algorithm": "yens", "rank": index + 1},
        )
        for index, path in enumerate(paths)
    ]

    return (
        {
            "algorithm": "yens",
            "requested_routes": k,
            "returned_routes": len(routes),
            "routes": routes,
            "comparison": compare_routes(routes),
        },
        200,
    )
