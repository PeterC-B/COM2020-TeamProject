import heapq
from math import inf
import networkx as nx


def astar(graph: nx.MultiDiGraph, source, target, cost_function, heuristic_function, trace=False):
    """
    A* search on a NetworkX MultiDiGraph.

    Parameters:
        graph: MultiDiGraph with edge attributes
        source: start node
        target: goal node
        cost_function: function(edge_data) -> cost
        heuristic_function: function(node) -> estimated cost to goal
        trace: enable debug logging

    Returns:
        (distance, path)
    """

    pq = [(0, source)]
    g_score = {source: 0}
    parent_of = {source: None}
    visited = set()

    def log(msg):
        if trace:
            print(msg)

    log(f"[START] A* from {source} to {target}")

    while pq:
        f_score, current = heapq.heappop(pq)
        log(f"[POP] node={current}, f_score={f_score}")

        if current in visited:
            continue

        visited.add(current)

        if current == target:
            log("[FOUND] Goal reached. Reconstructing path...")
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = parent_of[node]
            path.reverse()
            return g_score[target], path

        # Explore outgoing edges
        for _, neighbour, edge_data in graph.out_edges(current, data=True):
            weight = cost_function(edge_data)
            tentative_g = g_score[current] + weight

            if tentative_g < g_score.get(neighbour, inf):
                g_score[neighbour] = tentative_g
                parent_of[neighbour] = current

                h_value = heuristic_function(neighbour)
                new_f_score = tentative_g + h_value

                heapq.heappush(pq, (new_f_score, neighbour))

    return inf, []