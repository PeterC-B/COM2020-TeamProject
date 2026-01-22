import heapq
from math import inf, sqrt

"""
A* search on a weighted graph.
graph: {node: {neighbour: weight}}
heuristic_function: h(node) -> estimated cost to goal
Returns (distance, path)
"""
def astar(graph, source, target, heuristic_function, trace=False):

    pq = [(0, source)]      # priority queue
    g_score = {source: 0}       # cost from start to node
    parent_of = {source: None}      # for path reconstruction
    visited = set()

    def log(msg):
        if trace:
            print(msg)

    log(f"[START] A* from {source} to {target}")

    while pq:
        f_score, current_node = heapq.heappop(pq)
        log(f"[POP] node = {current_node}, f_score = {f_score}, g_score = {g_score.get(current_node, inf)}")

        if current_node in visited:
            log(f"  [SKIP] {current_node} already visited")
            continue

        visited.add(current_node)

        # Goal reached
        if current_node == target:
            log(f"[FOUND] Goal {target} reached. Reconstructing path...")

            path = []
            node = current_node
            while node is not None:
                path.append(node)
                node = parent_of[node]

            path.reverse()
            log(f"[PATH] {path}, total distance = {g_score[target]}")
            return g_score[target], path

        # Explore neighbours
        for neighbour, weight in graph.get(current_node, {}).items():
            tentative_g = g_score[current_node] + weight
            log(f"  [EDGE] {current_node} -> {neighbour} (weight = {weight}), tentative_g = {tentative_g}")

            if tentative_g < g_score.get(neighbour, inf):
                g_score[neighbour] = tentative_g
                parent_of[neighbour] = current_node

                h_value = heuristic_function(neighbour)
                new_f_score = tentative_g + h_value

                heapq.heappush(pq, (new_f_score, neighbour))
                log(f"    [UPDATE] {neighbour}: g_value = {tentative_g}, h_value = {h_value}, f_score = {new_f_score}")

    log("[FAIL] No path found")
    return inf, []

"""
Euclidean Heuristic Factory
Returns a heuristic function h(node) that computes
Euclidean distance from node to goal using coords dict.
"""
def ehf(coords, target):

    def heuristic(node):
        x1, y1 = coords[node]
        x2, y2 = coords[target]
        return sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return heuristic

# Example
if __name__ == "__main__":

    graph = {
        "A": {"B": 1, "C": 5},
        "B": {"C": 1, "D": 2},
        "C": {"D": 1},
        "D": {}
    }

    coords = {
        "A": (0, 0),
        "B": (1, 0),
        "C": (1, 1),
        "D": (2, 1)
    }

    heuristic = ehf(coords, target="D")

    print("Running A*...\n")

    distance, path = astar(
        graph = graph,
        source = "A",
        target = "D",
        heuristic_function = heuristic,
        trace = True
    )

    print("\nFinal A* result:")
    print("Distance:", distance)
    print("Path:", path)