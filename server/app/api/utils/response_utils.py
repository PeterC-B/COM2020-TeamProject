"""
Response utilities:
    - Standard API response formatting
    - Route comparison summaries
"""

import networkx as nx
import osmnx as ox
from server.app.domain.indicators.attribute_extraction import attach_edge_indicators

def compute_path_distance(graph: nx.MultiDiGraph, path):
    """Compute total distance along a path in a MultiDiGraph."""
    total = 0.0

    for u, v in zip(path[:-1], path[1:]):
        edge_data = graph.get_edge_data(u, v)

        if not edge_data:
            continue

        # Use the first edge key (OSMnx graphs rarely have parallel edges)
        first_key = next(iter(edge_data))
        total += edge_data[first_key].get("length", 0.0)

    return total

def compute_indicator_summary(graph:nx.MultiDiGraph, path, weights):
    """
    Compute average indicator values and weighted score for a route.
    """

    totals = {
        "lighting": 0.0,
        "greenery": 0.0,
        "pollution": 0.0,
        "surface_quality": 0.0,
        "amenity_proximity": 0.0,
    }

    edge_count = 0
    weighted_score = 0.0

    for u, v in zip(path[:-1], path[1:]):
        edge_data = graph.get_edge_data(u, v)
        if not edge_data:
            continue

        first_key = next(iter(edge_data))
        data = edge_data[first_key]

        if edge_count == 0:
            print(data)

        # Sum indicators
        for key in totals:
            if edge_count == 0:
                print(key)
            totals[key] += data.get(key, 0.0)

        if edge_count == 0:
            print(totals)

        # Weighted score
        for key, w in weights.items():
            if key == "distance":
                continue  # distance handled separately
            if key in data:
                weighted_score += data[key] * w

        print(edge_count)
        edge_count += 1

    if edge_count == 0:
        return {}

    # Compute averages
    averages = {k: v / edge_count for k, v in totals.items()}
    averages["weighted_score"] = weighted_score

    return averages


def build_geometry_from_graph(graph: nx.MultiDiGraph, path):
    """Return list of (lat, lon) for each node in the path."""
    geometry = []

    for node in path:
        data = graph.nodes[node]
        lat = data.get("y")
        lon = data.get("x")

        if lat is not None and lon is not None:
            geometry.append((lat, lon))

    return geometry


def format_route_response(path, graph, geometry=None, metadata=None, weights=None):
    """
    Format a single route response for the API.

    Parameters:
        path: list of node IDs
        graph: NetworkX MultiDiGraph
        geometry: optional list of (lat, lon)
        metadata: optional dict

    Returns:
        dict formatted for JSON response
    """
    total_distance = compute_path_distance(graph, path)

    if geometry is None:
        geometry = build_geometry_from_graph(graph, path)

    nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)

    edges_gdf = attach_edge_indicators(edges_gdf)

    graph = ox.graph_from_gdfs(nodes_gdf, edges_gdf)

    indicators = {}
    if weights is not None:
        indicators = compute_indicator_summary(graph, path, weights)

    return {
        "path": path,
        "distance": total_distance,
        "geometry": geometry,
        "indicators": indicators,
        "metadata": metadata or {}
    }



def compare_routes(routes):
    """
    Generate comparison metrics for multiple routes.

    Parameters:
        routes: list of dicts from format_route_response()

    Returns:
        dict summarising:
            - count
            - shortest_distance
            - longest_distance
            - average_distance
    """

    if not routes:
        return {
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