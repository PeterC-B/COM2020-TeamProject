import heapq
import copy
from math import inf
import networkx as nx
from server.app.domain.routing.algorithms.dijkstra_algorithm import dijkstra


def compute_path_cost(graph: nx.MultiDiGraph, path, cost_function):
    """Compute total cost of a path using the cost function."""
    total = 0
    for u, v in zip(path, path[1:]):
        # Use the first edge if multiple parallel edges exist
        edge_data = graph.get_edge_data(u, v)
        if not edge_data:
            return inf
        # edge_data is a dict of keys -> attributes
        first_key = next(iter(edge_data))
        total += cost_function(edge_data[first_key])
    return total


def yens_old(graph: nx.MultiDiGraph, source, target, k_paths, cost_function, trace=False):
    """
    Compute the K shortest loopless paths between two nodes in a NetworkX MultiDiGraph
    using Yen's algorithm

    This implementation generates k simple (cycle-free) paths in increasing order
    of total cost. It relies on Dijkstra's algorithm to compute spur paths and
    supports multigraphs with parallel directed edges. Edge weights are derived
    from the cost function

    :type graph: nx.MultiDiGraph: the directed multigraph to search
    :param source: the starting node for the search
    :param target: the goal node to reach
    :param k_paths: the number of shrotest loopless paths to return
    :param cost_function: a function that accepts a single edge attribute dictionary
    and returns the traversal cost for that edge
    :param trace: when true prints debug outputs

    Returns:
        list of lists
            A list of up to "k_paths" shortest loopless paths. Each path is a list of
            nodes from "source" to "target".
    """

    def log(msg):
        if trace:
            print(msg)

    log(f"[START] Yen's Algorithm from {source} to {target}, K={k_paths}")

    # First shortest path
    dist, first_path = dijkstra(graph, source, target, cost_function, trace=False)
    if not first_path:
        return []

    shortest_paths = [first_path]
    candidate_paths = []

    log(f"[P1] First shortest path: {first_path}")

    # Generate K-1 additional paths
    for k in range(1, k_paths):
        prev_path = shortest_paths[-1]

        for i in range(len(prev_path) - 1):
            spur_node = prev_path[i]
            root_path = prev_path[:i + 1]

            log(f"[SPUR] spur_node={spur_node}, root_path={root_path}")

            # Copy graph for modification
            graph_copy = copy.deepcopy(graph)

            # Remove edges that would recreate previous paths
            for p in shortest_paths:
                if len(p) > i and p[:i + 1] == root_path:
                    u = p[i]
                    v = p[i + 1]
                    if graph_copy.has_edge(u, v):
                        log(f"  [REMOVE EDGE] {u} -> {v}")
                        graph_copy.remove_edge(u, v)

            # Remove root path nodes except spur node
            for root_node in root_path[:-1]:
                if graph_copy.has_node(root_node):
                    log(f"  [REMOVE NODE] {root_node}")
                    graph_copy.remove_node(root_node)

            # Compute spur path
            spur_dist, spur_path = dijkstra(graph_copy, spur_node, target, cost_function, trace=False)

            if spur_path:
                total_path = root_path[:-1] + spur_path
                total_cost = compute_path_cost(graph, total_path, cost_function)
                log(f"  [CANDIDATE] {total_path} cost={total_cost}")
                heapq.heappush(candidate_paths, (total_cost, total_path))

        if not candidate_paths:
            break

        _, next_path = heapq.heappop(candidate_paths)
        shortest_paths.append(next_path)
        log(f"[P{k+1}] Next shortest path: {next_path}")

    return shortest_paths


def compute_path_length(graph, path):   # helper
    total = 0
    for from_node, to_node in zip(path, path[1:]):
        if from_node in graph and to_node in graph[from_node]:
            total += graph[from_node][to_node]
    return total

# Yen's K-shortest loopless paths
def yens(graph, source, target, k_paths = 3, trace=False):
    original_graph = copy.deepcopy(graph)

    def log(msg):
        if trace:
            print(msg)

    log(f"[START] Yen's Algorithm from {source} to {target}, K = {k_paths}")

    # First shortest path
    initDist, initPath = dijkstra(graph, source, target, trace=trace)
    if not initPath:
        log("[FAIL] No initial shortest path found")
        return []

    shortest_paths = [initPath]
    candidate_paths = []             

    log(f"[P1] First shortest path: {initPath}")

    # Generate K-1 additional paths
    for path_index in range(1, k_paths):
        log(f"\n[ITERATION] path_index = {path_index}")
        prev_path = shortest_paths[path_index - 1]

        # Spur each node in the previous path
        for spur_index in range(len(prev_path) - 1):
            spur_node = prev_path[spur_index]
            root_path = prev_path[:spur_index + 1]

            log(f"\n[SPUR] spur_index = {spur_index}, spur_node = {spur_node}, root_path = {root_path}")

            removed_edges = []
            removed_nodes = set()

            # Remove edges that recreate previous paths
            for existing_path in shortest_paths:
                if len(existing_path) > spur_index and existing_path[:spur_index + 1] == root_path:
                    from_node = existing_path[spur_index]
                    to_node = existing_path[spur_index + 1]
                    if to_node in graph.get(from_node, {}):
                        log(f"  [REMOVE EDGE] {from_node} -> {to_node}")
                        removed_edges.append((from_node, to_node, graph[from_node][to_node]))
                        del graph[from_node][to_node]

            # Remove root-path nodes except spur node
            for root_node in root_path[:-1]:
                if root_node in graph:
                    log(f"  [REMOVE NODE] {root_node}")
                    removed_nodes.add(root_node)
                    for neighbor, weight in list(graph[root_node].items()):
                        removed_edges.append((root_node, neighbor, weight))
                    del graph[root_node]

            # Run Dijkstra from spur node
            spur_dist, spur_path = dijkstra(graph, spur_node, target, trace=trace)

            if spur_path:
                total_path = root_path[:-1] + spur_path
                total_dist = compute_path_length(original_graph, total_path)
                log(f"  [CANDIDATE] path = {total_path}, distance = {total_dist}")
                heapq.heappush(candidate_paths, (total_dist, total_path))
            else:
                log("  [NO SPUR PATH]")

            # Restore graph
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
        log(f"[P{path_index+1}] Next shortest path: {next_path}")
        shortest_paths.append(next_path)

    return shortest_paths