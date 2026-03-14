import math

def get_nearest_node(graph, coords):
    """
    Pure test-only version of nearest-node lookup.
    Matches the behaviour expected by the tests.
    """
    lat, lon = coords

    best_node = None
    best_dist = math.inf

    for node_id, data in graph.nodes(data=True):
        nlat = data.get("y")
        nlon = data.get("x")

        # Skip nodes without coordinates
        if nlat is None or nlon is None:
            continue

        # Squared Euclidean distance (same behaviour as production)
        d = (lat - nlat) ** 2 + (lon - nlon) ** 2

        if d < best_dist:
            best_dist = d
            best_node = node_id

    if best_node is None:
        # Tests expect ValueError, not backend NotFoundError
        raise ValueError("No nodes with valid coordinates")

    return best_node
