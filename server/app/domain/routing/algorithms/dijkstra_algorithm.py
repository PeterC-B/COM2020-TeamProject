import heapq
from math import inf
import networkx as nx


def dijkstra(graph: nx.MultiDiGraph, source, target, cost_function, trace=False):
    """
    Dijkstra's algorithm on a NetworkX MultiDiGraph.

    Parameters:
        graph: MultiDiGraph with edge attributes
        source: start node
        target: goal node
        cost_function: function(edge_data) -> cost
        trace: enable debug logging

    Returns:
        (distance, path)
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