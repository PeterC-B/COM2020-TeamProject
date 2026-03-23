"""
Response utilities:
    - Standard API response formatting
    - Route comparison summaries
"""

import networkx as nx
import osmnx as ox
from app.domain.indicators.attribute_extraction import attach_edge_indicators
from scripts.visualisation.visualisation_utils import add_lighting_tag, add_surface_tag

def compute_path_distance(graph: nx.MultiDiGraph, path):
    """Compute total distance along a path in a MultiDiGraph."""
    total = 0.0

    for u, v in zip(path[:-1], path[1:]):
        edge_data = graph.get_edge_data(u, v)

        if not edge_data:
            continue

        # Use the first edge key (OSMnx graphs rarely have parallel edges)
        first_key = next(iter(edge_data))
        total += edge_data[first_key].get("distance", 0.0)

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
    }

    edge_count = 0
    weighted_score = 0.0
    accessible = True

    for u, v in zip(path[:-1], path[1:]):
        edge_data = graph.get_edge_data(u, v)
        if not edge_data:
            continue
            
        all_weights = []
        for weights in edge_data.values():
            all_weights.append(weights["weight"])

        weighted_score += min(all_weights)
                
        first_key = next(iter(edge_data))
        data = edge_data[first_key]

        if(data.get("accessible") == False):
            accessible = False

        # Sum indicators
        for key in totals:
            totals[key] += data.get(key, 0.0)

        # Weighted score
        '''for key, w in weights.items():
            if key == "distance":
                continue  # distance handled separately
            if key in data:
                weighted_score += data[key] * w'''

        edge_count += 1

    if edge_count == 0:
        return {}

    # Compute averages
    averages = {k: v / edge_count for k, v in totals.items()}
    averages["weighted_score"] = weighted_score
    averages["accessible"] = accessible

    return averages


def build_geometry_from_graph(graph: nx.MultiDiGraph, path):
    """
    Build a route geometry using edge geometries instead of node straight lines.
    Returns list of (lat, lon) coordinates.
    """

    geometry = []

    for u, v in zip(path[:-1], path[1:]):
        edge_data = graph.get_edge_data(u, v)

        if not edge_data:
            continue

        first_key = next(iter(edge_data))
        data = edge_data[first_key]

        if "geometry" in data:
            line = data["geometry"]

            xs, ys = line.xy

            coords = list(zip(ys, xs))

            if geometry and geometry[-1] == coords[0]:
                geometry.extend(coords[1:])
            else:
                geometry.extend(coords)

        else:
            u_data = graph.nodes[u]
            v_data = graph.nodes[v]

            u_coord = (u_data["y"], u_data["x"])
            v_coord = (v_data["y"], v_data["x"])

            if not geometry:
                geometry.append(u_coord)

            geometry.append(v_coord)

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

    if "crs" not in graph.graph:
        graph.graph["crs"] = "EPSG:4326"

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