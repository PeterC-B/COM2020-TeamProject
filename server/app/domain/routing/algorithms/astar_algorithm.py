import heapq
from math import inf
import networkx as nx


def astar(graph: nx.MultiDiGraph, source, target, cost_function, heuristic_function, trace=False):
    """
    Performs an A* search on a NetworkX MultiDiGraph

    This implementation computes the lowest_cost path from a start node to a
    target node using pre-defined cost and heuristic functions. It supports
    graphs with mutiple directed edges between nodes and allows for edge weights
    to be derived from arbitrary attributes.
    
    :type graph: nx.MultiDiGraph : the directed multigraph to search
    :param source: the starting node for the search
    :param target: the goal node to reach
    :param cost_function: a function that accepts a single edge attribute dictionary
    and returns the traversal cost for that edge
    :param heuristic_function: a function that accepts a node and returns a heuristic estimate
    of the remaining cost to the target
    :param trace: when true prints debug outputs

    Returns:
    tuple
        A pair (distance, path) where:
            - "distance" is the total cost of the optimal path
            - "path" is a list of nodes representing the optimal route between
              source and target.
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