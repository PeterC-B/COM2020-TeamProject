"""
Node utility function:
    - Nearest-node lookup
    - Conversion between lat/lon and graph nodes
"""

def get_nearest_node(graph, coords):
    """
    Return the nearest graph node to the given (lat, lon) coordinates
    
    :param graph: adjacency dict (routing graph)
    :param coords: (lat, lon)

    Returns:
        nearest_node_id
    """

    lat, lon = coords

    """
    Should extract node coordinates from routing graph
    graph[node] must contain a "coords" entry or you must pass in a seperate coordinate map
    However current routing graph does not store coords
    Key: "__coords__" is used in place
    """

    coord_map = graph.get("__coords__")

    if coord_map is None:
        raise ValueError(
            "Routing graph does not contain '__coords__'"
            "Ensure extract_node_coordinates() was used and stored"
        )
    
    # Find nearest node by Euclidean distance in lat/lon space
    best_node = None
    best_dist = float("inf")

    for node_id, (nlat, nlon) in coord_map.items():
        d = (lat - nlat) ** 2 + (lon - nlon) ** 2
        if d < best_dist:
            best_dist = d
            best_node = node_id
    
    return best_node
