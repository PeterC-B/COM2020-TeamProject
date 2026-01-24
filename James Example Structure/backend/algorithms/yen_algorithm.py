import heapq
import copy
from math import inf

def dijkstra(graph, source, target, trace=False):
    pq = [(0, source)]      # priority queue
    dist = {source: 0}
    parent = {source: None}
    visited = set()

    def log(msg):
        if trace:
            print(msg)

    log(f"[START] Dijkstra from {source} to {target}")

    while pq:
        curr_dist, curr_node = heapq.heappop(pq)
        log(f"[POP] node = {curr_node}, distance = {curr_dist}")

        if curr_dist > dist.get(curr_node, inf):
            log(f"  [SKIP] stale entry for {curr_node}")
            continue

        if curr_node in visited:
            log(f"  [SKIP] {curr_node} already visited")
            continue

        visited.add(curr_node)

        if curr_node == target:
            log(f"[FOUND] Goal {target} reached. Reconstructing path...")

            path = []
            node = curr_node
            while node is not None:
                path.append(node)
                node = parent[node]

            path.reverse()
            log(f"[PATH] {path}, total distance = {curr_dist}")
            return curr_dist, path

        for neighbor, weight in graph.get(curr_node, {}).items():
            new_dist = curr_dist + weight
            log(f"  [EDGE] {curr_node} -> {neighbor} (weight = {weight}), new_distance = {new_dist}")

            if new_dist < dist.get(neighbor, inf):
                dist[neighbor] = new_dist
                parent[neighbor] = curr_node
                heapq.heappush(pq, (new_dist, neighbor))
                log(f"    [UPDATE] {neighbor}: distance = {new_dist}, parent = {curr_node}")

    log("[FAIL] No path found")
    return inf, []

def compute_path_length(graph, path):   # helper
    total = 0
    for from_node, to_node in zip(path, path[1:]):
        total += graph[from_node][to_node]
    return total

# Yen's K-shortest loopless paths
def yens(graph, source, target, k_paths, trace=False):
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

# Example
if __name__ == "__main__":

    graph = {
    "N1": {"N2": 7, "N3": 12, "N4": 5, "N5": 9},
    "N2": {"N6": 3, "N7": 14, "N8": 6},
    "N3": {"N7": 4, "N8": 11, "N9": 8},
    "N4": {"N8": 10, "N9": 2, "N10": 13},
    "N5": {"N9": 7, "N10": 4, "N11": 15},

    "N6": {"N12": 6, "N13": 9, "N14": 3},
    "N7": {"N13": 5, "N14": 12, "N15": 8},
    "N8": {"N14": 7, "N15": 10, "N16": 4},
    "N9": {"N15": 6, "N16": 9, "N17": 11},
    "N10": {"N16": 8, "N17": 5, "N18": 14},
    "N11": {"N17": 7, "N18": 12, "N19": 6},

    "N12": {"N20": 4, "N21": 11, "N22": 9},
    "N13": {"N21": 6, "N22": 13, "N23": 5},
    "N14": {"N22": 7, "N23": 10, "N24": 8},
    "N15": {"N23": 9, "N24": 6, "N25": 12},
    "N16": {"N24": 5, "N25": 11, "N26": 7},
    "N17": {"N25": 8, "N26": 14, "N27": 6},
    "N18": {"N26": 9, "N27": 4, "N28": 15},
    "N19": {"N27": 10, "N28": 7, "N29": 12},

    "N20": {"N30": 6, "N31": 8, "N32": 11},
    "N21": {"N31": 7, "N32": 10, "N33": 4},
    "N22": {"N32": 9, "N33": 6, "N34": 12},
    "N23": {"N33": 5, "N34": 14, "N35": 7},
    "N24": {"N34": 8, "N35": 9, "N36": 11},
    "N25": {"N35": 6, "N36": 13, "N37": 5},
    "N26": {"N36": 7, "N37": 10, "N38": 8},
    "N27": {"N37": 9, "N38": 6, "N39": 12},
    "N28": {"N38": 5, "N39": 11, "N40": 7},
    "N29": {"N39": 8, "N40": 10, "N41": 6},

    "N30": {"N42": 9, "N43": 6, "N44": 12},
    "N31": {"N43": 7, "N44": 5, "N45": 11},
    "N32": {"N44": 8, "N45": 10, "N46": 6},
    "N33": {"N45": 9, "N46": 7, "N47": 13},
    "N34": {"N46": 5, "N47": 12, "N48": 8},
    "N35": {"N47": 6, "N48": 9, "N49": 14},
    "N36": {"N48": 7, "N49": 11, "N50": 5},
    "N37": {"N49": 8, "N50": 10, "N51": 6},
    "N38": {"N50": 9, "N51": 7, "N52": 12},
    "N39": {"N51": 6, "N52": 8, "N53": 11},
    "N40": {"N52": 10, "N53": 5, "N54": 9},
    "N41": {"N53": 7, "N54": 12, "N55": 6},

    "N42": {"N56": 8, "N57": 11, "N58": 6},
    "N43": {"N57": 7, "N58": 10, "N59": 5},
    "N44": {"N58": 9, "N59": 6, "N60": 12},
    "N45": {"N59": 8, "N60": 11, "N61": 7},
    "N46": {"N60": 5, "N61": 13, "N62": 9},
    "N47": {"N61": 6, "N62": 10, "N63": 8},
    "N48": {"N62": 7, "N63": 9, "N64": 12},
    "N49": {"N63": 5, "N64": 11, "N65": 6},
    "N50": {"N64": 8, "N65": 10, "N66": 7},
    "N51": {"N65": 9, "N66": 6, "N67": 12},
    "N52": {"N66": 5, "N67": 11, "N68": 8},
    "N53": {"N67": 7, "N68": 10, "N69": 6},
    "N54": {"N68": 9, "N69": 12, "N70": 5},
    "N55": {"N69": 8, "N70": 7, "N71": 11},

    "N56": {"N72": 6, "N73": 9, "N74": 12},
    "N57": {"N73": 7, "N74": 10, "N75": 5},
    "N58": {"N74": 8, "N75": 11, "N76": 6},
    "N59": {"N75": 9, "N76": 7, "N77": 13},
    "N60": {"N76": 5, "N77": 12, "N78": 8},
    "N61": {"N77": 6, "N78": 9, "N79": 14},
    "N62": {"N78": 7, "N79": 10, "N80": 5},
    "N63": {"N79": 8, "N80": 11, "N81": 6},
    "N64": {"N80": 9, "N81": 7, "N82": 12},
    "N65": {"N81": 6, "N82": 10, "N83": 8},
    "N66": {"N82": 7, "N83": 9, "N84": 11},
    "N67": {"N83": 5, "N84": 12, "N85": 6},
    "N68": {"N84": 8, "N85": 10, "N86": 7},
    "N69": {"N85": 9, "N86": 6, "N87": 12},
    "N70": {"N86": 5, "N87": 11, "N88": 8},
    "N71": {"N87": 7, "N88": 10, "N89": 6},

    "N72": {"N90": 9, "N91": 6, "N92": 12},
    "N73": {"N91": 7, "N92": 10, "N93": 5},
    "N74": {"N92": 8, "N93": 11, "N94": 6},
    "N75": {"N93": 9, "N94": 7, "N95": 13},
    "N76": {"N94": 5, "N95": 12, "N96": 8},
    "N77": {"N95": 6, "N96": 9, "N97": 14},
    "N78": {"N96": 7, "N97": 10, "N98": 5},
    "N79": {"N97": 8, "N98": 11, "N99": 6},
    "N80": {"N98": 9, "N99": 7, "N100": 12},
    "N81": {"N99": 6, "N100": 10},
    "N82": {"N100": 8},
    "N83": {"N100": 7},
    "N84": {"N100": 9},
    "N85": {"N100": 11},
    "N86": {"N100": 6},
    "N87": {"N100": 13},
    "N88": {"N100": 5},
    "N89": {"N100": 14},
    "N90": {"N100": 10},
    "N91": {"N100": 12},
    "N92": {"N100": 9},
    "N93": {"N100": 8},
    "N94": {"N100": 7},
    "N95": {"N100": 6},
    "N96": {"N100": 11},
    "N97": {"N100": 5},
    "N98": {"N100": 10},
    "N99": {"N100": 4},
    "N100": {}
}

    # Compute the 3 shortest loopless paths from A to D
    k_value = 3
    source = "N1"
    target = "N100"

    print(f"Computing {k_value} shortest paths from {source} to {target}...\n")

    paths = yens(
        graph = graph,
        source = source,
        target = target,
        k_paths = k_value,
        trace = False
    )

    print("\nFinal K shortest paths:")
    for index, path in enumerate(paths, start = 1):
        print(f"{index}: {path}")