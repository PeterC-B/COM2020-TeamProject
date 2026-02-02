"""
Geometry utilities for routing and frontend visualisation.
"""

def extract_node_coordinates(graph):
    """
    Return a dict mapping node_id -> (lat, lon)
    """
    coords = {}

    for node_id, data in graph.nodes(data=True):
        lat = data.get("y")
        lon = data.get("x")

        if lat is not None and lon is not None:
            coords[node_id] = (lat, lon)

    return coords