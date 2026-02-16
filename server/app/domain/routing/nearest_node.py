"""
Nearest-node lookup utilities for routing.

Works directly on a NetworkX MultiDiGraph that contains
OSMnx-style node attributes:
    - node["x"] = longitude
    - node["y"] = latitude
"""

import networkx as nx
from math import inf

from server.app.domain.errors import NotFoundError


def get_nearest_node(graph: nx.MultiDiGraph, coords: tuple):
    """
    Return the nearest graph node to the given (lat, lon) coordinates.

    Parameters:
        graph: NetworkX MultiDiGraph
        coords: (lat, lon)

    Returns:
        nearest_node_id
    """

    lat, lon = coords

    best_node = None
    best_dist = inf

    # Loop through all nodes and compute squared Euclidean distance
    for node_id, data in graph.nodes(data=True):
        nlat = data.get("y")
        nlon = data.get("x")

        if nlat is None or nlon is None:
            continue  # skip nodes without coordinates

        d = (lat - nlat) ** 2 + (lon - nlon) ** 2

        if d < best_dist:
            best_dist = d
            best_node = node_id

    if best_node is None:
        raise NotFoundError(message="No nodes in graph contain coordinate data")

    return best_node

if __name__ == "__main__":
    from server.app.domain.routing.graph_loader import load_graph_from_disk
    graph = load_graph_from_disk()
    print(get_nearest_node(graph, (51.460498, -2.585757)))
