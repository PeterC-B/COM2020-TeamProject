"""
Visualisation Utilities:
    - Plot shortest path on an OSMnx graph
    - Plot crime heatmap
    - Plot blank or feature-filled graphs for debugging/visualisation
"""

import osmnx as ox
import networkx as nx
import geopandas as gpd
import matplotlib.cm as cm
import matplotlib.colors as mcolors


# -------------------------------------------------------------------
# Local visualisation-only helpers (kept out of backend logic)
# -------------------------------------------------------------------

def add_crime_rating(edges_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Convert access_score into a colour-coded crime heatmap.
    This is a visualisation-only helper.
    """

    def score_band(d):
        if d < 0.001: return 1
        elif d < 0.0059: return 0.9
        elif d < 0.0108: return 0.8
        elif d < 0.0157: return 0.7
        elif d < 0.0206: return 0.6
        elif d < 0.0255: return 0.5
        elif d < 0.0304: return 0.4
        elif d < 0.0353: return 0.3
        elif d < 0.0402: return 0.2
        elif d < 0.0451: return 0.1
        else: return 0

    edges_gdf["score_band"] = edges_gdf["access_score"].fillna(0).apply(score_band)

    cmap = cm.get_cmap("RdYlGn")
    edges_gdf["edge_colour"] = edges_gdf["score_band"].apply(
        lambda x: mcolors.to_hex(cmap(x))
    )

    return edges_gdf


def add_feature_to_graph(graph, ax, coords, feature):
    """
    Visualisation-only helper for plotting POIs on a graph.
    """

    features = ox.features_from_point(
        center_point=coords,
        tags=feature[1],
        dist=450,
    )

    # Limit amenities for readability
    if feature[0] == "Amenities" and len(features) > 80:
        features = features.sample(n=80, random_state=42)

    features["centroid"] = features.geometry.centroid

    features.plot(
        ax=ax,
        color=feature[2],
        label=feature[0],
        alpha=feature[3],
        markersize=feature[4],
    )


# -------------------------------------------------------------------
# Visualisation functions
# -------------------------------------------------------------------

def print_shortest_path_graph(graph: nx.MultiDiGraph,
                              node_path: list,
                              savingFilePath: str = "graphs/png/shortest_path.png"):
    """
    Plot a graph with the shortest path highlighted.
    """

    nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)

    # Default styling
    edges_gdf["edge_colour"] = "#CCCCCC"
    edges_gdf["edge_alpha"] = 0.4
    nodes_gdf["node_colour"] = "#FFFFFF"
    nodes_gdf["node_size"] = 15
    nodes_gdf["node_alpha"] = 0.4

    # Highlight path edges
    path_edges = list(zip(node_path[:-1], node_path[1:]))

    for u, v in path_edges:
        mask = (edges_gdf["u"] == u) & (edges_gdf["v"] == v)
        edges_gdf.loc[mask, "edge_colour"] = "#0000FF"
        edges_gdf.loc[mask, "edge_alpha"] = 1.0

    # Highlight start/end nodes
    nodes_gdf.loc[node_path[0], ["node_colour", "node_size", "node_alpha"]] = ["#FF0000", 35, 1]
    nodes_gdf.loc[node_path[-1], ["node_colour", "node_size", "node_alpha"]] = ["#FF0000", 35, 1]

    # Rebuild graph with styling
    styled_graph = ox.graph_from_gdfs(nodes_gdf, edges_gdf)

    fig, ax = ox.plot_graph(
        styled_graph,
        edge_color=edges_gdf["edge_colour"],
        edge_alpha=edges_gdf["edge_alpha"],
        node_color=nodes_gdf["node_colour"],
        node_size=nodes_gdf["node_size"],
        node_alpha=nodes_gdf["node_alpha"],
        show=False,
        close=False
    )

    fig.savefig(savingFilePath, dpi=300)


def plot_crime_graph(graph: nx.MultiDiGraph,
                     filePath: str = "graphs/png/crime_graph.png"):
    """
    Plot a crime heatmap based on access_score.
    """

    nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)
    edges_gdf = add_crime_rating(edges_gdf)

    fig, ax = ox.plot_graph(
        graph,
        edge_color=edges_gdf["edge_colour"],
        edge_linewidth=2,
        show=False,
        close=False,
    )

    fig.savefig(filePath, dpi=300)


def plot_blank_graph(coords: tuple,
                     radius: int,
                     travel_type: str,
                     saveToFile: bool = False,
                     filePath: str = "graphs/png/blank_graph.png"):
    """
    Plot a blank graph for debugging.
    """

    graph = ox.graph_from_point(
        center_point=coords,
        dist=radius,
        network_type=travel_type,
    )

    fig, ax = ox.plot_graph(graph, show=False, close=False)

    if saveToFile:
        fig.savefig(filePath, dpi=300)

    return graph


def plot_filled_graph(features: list,
                      coords: tuple,
                      radius: int,
                      travel_type: str,
                      saveToFile: bool = False,
                      incLegend: bool = False,
                      filePath: str = "graphs/png/filled_graph.png"):
    """
    Plot a graph with features (POIs) added.
    """

    graph = plot_blank_graph(coords, radius, travel_type)
    fig, ax = ox.plot_graph(graph, show=False, close=False)

    for feature in features:
        add_feature_to_graph(graph, ax, coords, feature)

    if incLegend:
        ax.legend()

    if saveToFile:
        fig.savefig(filePath, dpi=300)

    return graph