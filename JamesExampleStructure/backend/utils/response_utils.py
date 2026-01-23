"""
Response utilities:
    - Standard API response formatting
    - Error formatting
    - Route comparison summaries
"""

from flask import jsonify

# Format a single route response for the API
def format_route_response(path, graph, geometry=None, metadata=None):
    """
    Format a single route response for the API
    
    :param path: list of node IDs
    :param graph: adjacency dict (routing graph)
    :param geometry: optional list of (lat, lon) coordinates
    :param metadata: optional dict of extra info

    Returns:
        dict formatted for JSON response
    """

    # Compute total distance from graph
    total_distance = 0.0
    for u, v in zip(path[:-1], path[1:]):
        total_distance += graph[u][v].get("distance", 0)
    
    # If geometry not provided, build from node coordinates
    if geometry is None:
        coords = graph.get("__coords__", {})
        geometry = [coords[n] for n in path if n in coords]

    return {
        "path": path,
        "distance": total_distance,
        "geometry": geometry,
        "metadata": metadata or {}
    }


# Return a standardised error response
def format_error(message, status=400):
    response = jsonify({"error": message})
    response.status_code = status
    return response

def compare_routes(routes):
    """
    Generate comparison metrics for multiple routes
    
    :param routes: list of route dicts produced by format_route_response()

    Returns:
        dict summarising:
            - shortest distance
            - longest distance
            - average distance
            - number of routes
    """

    if not routes:
        return  {
            "count": 0,
            "shortest_distance": None,
            "longest_distance": None,
            "average_distance": None
        }
    
    distances = [r["distance"] for r in routes]

    return {
        "count": len(routes),
        "shortest_distance": min(distances),
        "longest_distance": max(distances),
        "average_distance": sum(distances) / len(distances)
    }