import graph_modification as oxl
import file_reading as fle
import osmnx as ox
import pandas as pd
import networkx as nx
import geopandas as gpd
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib as mlt
from pyproj import Transformer
import numpy as np

def print_shortest_path_graph(graph : nx.MultiDiGraph, shortestPath : list, edgesCSVPath : str, savingFilePath : str = "mapping/graphs/shortestPathGraph.img"):
    '''
    Takes the shortest path (in-order by nodes) and saves a graph to a specified locaion with the shortest path highlighted.
    
    :param graph: The multidirectional graph containing the area that is being routed
    :type graph: nx.MultiDiGraph
    :param shortestPath: The list of in-order nodes of the shortest path
    :type shortestPath: list
    :param edgesCSVPath: The filepath of the CSV file that contains the information about the edges
    :type edgesCSVPath: str
    :param savingFilePath: The filepath where the graph should be saved to
    :type savingFilePath: str
    '''
    # Convert the graph to the GeoDataFrames and find the list of edges the shortest path takes
    edges_gdf, nodes_gdf = ox.graph_to_gdfs(graph)
    edgePath = oxl.edge_path_to_csv_rule(shortestPath, edgesCSVPath)

    # Copy the GDFs and set the standard colour of nodes and edges to white, and being a little transparent
    edges_temp = edges_gdf.copy()
    nodes_temp = nodes_gdf.copy()

    edges_temp["edge_colour"] = "#FFFFFF"
    nodes_temp["node_colour"] = "#FFFFFF"
    nodes_temp["node_size"] = 15
    nodes_temp["node_alpha"] = 0.4
    edges_temp["edge_alpha"] = 0.4

    # Set every edge in the shortest path to blue and fully visible
    for u, v, k in edgePath:
        edges_temp.loc[(u, v, k), "edge_colour"] = "#0000FF"
        edges_temp.loc[(v, u, k), "edge_colour"] = "#0000FF"
        edges_temp.loc[(u, v, k), "edge_alpha"] = 1
        edges_temp.loc[(v, u, k), "edge_alpha"] = 1

    # Find the first and last node in the path and make them red and easy to see
    osmid = shortestPath[0]
    nodes_temp.loc[osmid, "node_colour"] = "#FF0000"
    nodes_temp.loc[osmid, "node_size"] = 35
    nodes_temp.loc[osmid, "node_alpha"] = 1

    osmid = shortestPath[len(shortestPath)-1]
    nodes_temp.loc[osmid, "node_colour"] = "#FF0000"
    nodes_temp.loc[osmid, "node_size"] = 35
    nodes_temp.loc[osmid, "node_alpha"] = 1

    # Recreate the route graph from the GDFs with the colour formatting included
    routeGraph = ox.graph_from_gdfs(nodes_temp, edges_temp)

    # set lists for the colours, alphas and sizes of each edge in the graph
    edge_colours = [
        data.get("edge_colour", "#FFFFFF")
        for _, _, _, data in routeGraph.edges(keys=True, data=True)
    ]

    edge_alphas = [
        data.get("edge_alpha", "#FFFFFF")
        for _, _, _, data in routeGraph.edges(keys=True, data=True)
    ]

    node_colours = [
        data.get("node_colour", "#FFFFFF")
        for _, data in routeGraph.nodes(data=True)
    ]
    node_sizes = [
        data.get("node_size", 20)
        for _, data in routeGraph.nodes(data=True)
    ]
    node_alphas = [
        data.get("node_alpha", 1)
        for _, data in routeGraph.nodes(data=True)
    ]

    # Create the plot with the correct colouring
    fig1, ax1 = ox.plot_graph(
        routeGraph,
        edge_color=edge_colours,
        node_color=node_colours,
        node_size=node_sizes,
        node_alpha=node_alphas,
        edge_alpha=edge_alphas,
        show=False,
        close=False
    )

    # Save the plot to a file path as specified in the parameters
    fig1.savefig(savingFilePath, dpi=300)

def create_nodes_table(nodes_gdf : gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    '''
    Creates a readable table for the nodes GDF
    
    :param nodes_gdf: The GeoDataFrame containing all information on nodes
    :type nodes_gdf: gpd.GeoDataFrame
    :return: The created nodes table
    :rtype: GeoDataFrame
    '''
    nodes_table = nodes_gdf.reset_index()[[
        "osmid",
        "x",
        "y",
    ]]

    nodes_table = nodes_table.rename(columns={
        "osmid" : "node_id",
    })
    return nodes_table

def create_edges_table(edges_gdf : gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    '''
    Creates a readable table for the edges GDF
    
    :param edges_gdf: The GeoDataFrame containing all information on edges
    :type edges_gdf: gpd.GeoDataFrame
    :return: The created edges table
    :rtype: GeoDataFrame
    '''
    edges_table = edges_gdf.reset_index()[[
        "u", "v", "key",
        "length",
        "travel_time",
        "access_score",
    ]]

    edges_table = edges_table.rename(columns={
        "u":"from_node",
        "v":"to_node",
    })
    return edges_table

def add_crime_rating(edges_gdf : gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    '''
    Adds a HEX value to each edge denoting its proximity to a crime spot
    
    :param edges_gdf: The GeoDataFrame containing all information on edges
    :type edges_gdf: gpd.GeoDataFrame
    :return: The updated edge GeoDataFrame with the hex values for the crime heatmap included
    :rtype: GeoDataFrame
    '''
    def score_band(d):
        if d < 0.001:
            return 1
        elif d < 0.0059:
            return 0.9
        elif d < 0.0108:
            return 0.8
        elif d < 0.0157:
            return 0.7
        elif d < 0.0206:
            return 0.6
        elif d < 0.0255:
            return 0.5
        elif d < 0.0304:
            return 0.4
        elif d < 0.0353:
            return 0.3
        elif d < 0.0402:
            return 0.2
        elif d < 0.0451:
            return 0.1
        else:
            return 0

    edges_gdf["score_band"] = edges_gdf["access_score"].apply(score_band)

    cmap = cm.get_cmap("RdYlGn")

    edges_gdf["edge_colour"] = edges_gdf["score_band"].apply(
        lambda x: mcolors.to_hex(cmap(x))
    )
    return edges_gdf

def plot_crime_graph(graph : nx.MultiDiGraph, filePath : str = "mapping/graphs/crimeGraph.img"):
    '''
    Uses an algorithm to calculate crime spread across a graph and saves the crime heatmap as a picture
    
    :param graph: The multidirectional graph containing the area that is being routed
    :type graph: nx.MultiDiGraph
    :param filePath: The file path where the crime graph will be saved to
    :type filePath: str
    '''
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

def plot_blank_graph(coords : tuple, radius : int, travel_type : str, saveToFile : bool = False, filePath : str = f"mapping/graphs/blank_graph.png") -> nx.MultiDiGraph:
    '''
    Create and saves the blank graph centered around coordinates from OSM with a designated radius
    
    :param coords: The coordinates of the center of the graph
    :type coords: tuple
    :param radius: The radius of the area being plotted
    :type radius: int
    :param travel_type: How the area is being traversed
    :type travel_type: str
    :param saveToFile: Whether the blank graph should be saved to a file or not
    :type saveToFile: bool
    :param filePath: The filepath to save the blank graph to
    :type filePath: str
    :return: The generated blank graph with nodes and edges attached
    :rtype: nx.MultiDiGraph
    '''
    graph = ox.graph_from_point(
        center_point=coords,
        dist=radius,
        network_type=travel_type,
    )
    graph = ox.add_edge_speeds(graph)
    graph = ox.add_edge_travel_times(graph)
    graph = ox.add_node_elevations_raster(graph, "bristol_raster.tif")

    fig, ax = get_figure_and_axes(graph)
    
    if(saveToFile):
        fig.savefig(filePath, dpi=300)
    return graph

def get_figure_and_axes(graph : nx.MultiDiGraph) -> tuple[Figure, Axes]:
    return ox.plot_graph(graph, show=False, close=False)

def plot_filled_graph(features : list, coords : tuple, radius : int, travel_type : str, saveToFile : bool = False, incLegend : bool = False, filePath : str = f"mapping/graphs/filled_graph.png") -> nx.MultiDiGraph:
    graph = plot_blank_graph(coords, radius, travel_type)
    fig, ax = get_figure_and_axes(graph)
    
    for feature in features:
        oxl.addFeatureToGraph(graph, ax, coords, feature)
    
    if(incLegend):
        ax.legend()

    if(saveToFile):
        fig.savefig(filePath, dpi=300)

    return graph

def create_graphml(graph : nx.MultiDiGraph):
    ox.save_graphml(graph, "bristol_elevation.graphml")

if __name__ == "__main__":
    graph = plot_blank_graph((51.460498, -2.585757), 450, "walk")
    create_graphml(graph)