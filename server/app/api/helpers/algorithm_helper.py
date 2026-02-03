from server.app.domain.routing.algorithms.yen_algorithm import yens
from server.app.domain.routing.algorithms.dijkstra_algorithm import dijkstra
import networkx as nx
import osmnx as ox

def get_dict_of_edges(graph : nx.MultiDiGraph):
    _, edges_gdf = ox.graph_to_gdfs(graph)
    edges_gdf = edges_gdf.reset_index()
    edges_gdf = edges_gdf[[
        "u", "v", "key",
        "length",
    ]]
    edges = edges_gdf.to_dict(orient="records")
    all_edges = {}
    for edge in edges:
        u = edge["u"]
        v = edge["v"]
        length = edge["length"]

        if u not in all_edges:
            all_edges[u] = {}

        all_edges[u][v] = length
    return all_edges