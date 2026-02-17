import copy
import heapq
import math

def compute_path_length(graph, path):
    total = 0
    for u, v in zip(path, path[1:]):
        if u not in graph or v not in graph[u]:
            break
        total += graph[u][v]
    return total


def _dijkstra(graph, source, target):
    dist = {n: math.inf for n in graph}
    prev = {}
    dist[source] = 0
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if u == target:
            break
        if d > dist[u]:
            continue
        for v, w in graph.get(u, {}).items():
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))

    if dist[target] == math.inf:
        return math.inf, []

    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    path.reverse()
    return dist[target], path

def yens(graph, source, target, k_paths=3, trace=False):
    original = copy.deepcopy(graph)

    dist, path = _dijkstra(graph, source, target)
    if not path:
        return []

    shortest_paths = [path]
    candidates = []

    for k in range(1, k_paths):
        prev = shortest_paths[-1]

        for i in range(len(prev) - 1):
            spur = prev[i]
            root = prev[:i+1]

            removed_edges = []
            removed_nodes = set()

            for p in shortest_paths:
                if len(p) > i and p[:i+1] == root:
                    u = p[i]
                    v = p[i+1]
                    if v in graph.get(u, {}):
                        removed_edges.append((u, v, graph[u][v]))
                        del graph[u][v]

            for r in root[:-1]:
                if r in graph:
                    for v, w in list(graph[r].items()):
                        removed_edges.append((r, v, w))
                    removed_nodes.add(r)
                    del graph[r]

            spur_dist, spur_path = _dijkstra(graph, spur, target)

            if spur_path:
                total_path = root[:-1] + spur_path
                total_dist = compute_path_length(original, total_path)
                heapq.heappush(candidates, (total_dist, total_path))

            for u, v, w in removed_edges:
                graph.setdefault(u, {})[v] = w
            for n in removed_nodes:
                graph.setdefault(n, {})

        if not candidates:
            break

        _, next_path = heapq.heappop(candidates)
        shortest_paths.append(next_path)

    return shortest_paths
