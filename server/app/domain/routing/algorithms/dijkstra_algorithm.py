import heapq
from math import inf
import networkx as nx


def dijkstra(graph: nx.MultiDiGraph, source, target, cost_function, trace=False):
    """
    Computes the shortest path between two nodes in a NetworkX MultiDiGraph
    using Dijkstra's algorithm

    This implementation supports multigraphs with multiple directed edges
    between nodes and allows for use of edge weights to be derived from arbitrary
    attributes via the cost function
    
    :type graph: nx.MultiDiGraph: the directed multigraph to search
    :param source: the starting node for the search
    :param target: the goal node to reach
    :param cost_function: a function that accepts a single edge attribute dictionary
    and returns the traversal cost for that edge
    :param trace: when true prints debug outputs

    Returns:
    tuple
        A pair (distance, path) where:
            - "distance" is the total cost of the shortest path
            - "path" is a list of nodes representing the shortest route between
              source and target.
    """

    pq = [(0, source)]
    dist = {source: 0}
    parent = {source: None}
    visited = set()

    def log(msg):
        if trace:
            print(msg)

    log(f"[START] Dijkstra from {source} to {target}")

    while pq:
        curr_dist, curr_node = heapq.heappop(pq)
        log(f"[POP] node={curr_node}, dist={curr_dist}")

        if curr_node in visited:
            continue

        visited.add(curr_node)

        if curr_node == target:
            log("[FOUND] Goal reached. Reconstructing path...")
            path = []
            node = curr_node
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            return curr_dist, path

        # Explore outgoing edges
        for _, neighbour, edge_data in graph.out_edges(curr_node, data=True):
            weight = cost_function(edge_data)
            new_dist = curr_dist + weight

            if new_dist < dist.get(neighbour, inf):
                dist[neighbour] = new_dist
                parent[neighbour] = curr_node
                heapq.heappush(pq, (new_dist, neighbour))

    return inf, []