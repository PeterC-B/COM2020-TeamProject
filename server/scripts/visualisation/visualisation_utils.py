"""
Visualisation Utilities:
    - Plot shortest path on an OSMnx graph
    - Plot crime heatmap
    - Plot blank or feature-filled graphs for debugging/ visualisation
"""
import osmnx as ox
import networkx as nx
from graph.attribute_extraction import add_crime_rating, add_feature_to_graph

def print_shortest_path_graph(graph : nx.MultiDiGraph, 
                              node_path : list, 
                              savingFilePath: str = "graphs/png/shortest_path.png"):
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

    # Highlight a shortest path on an OSMnx graph and save the image
    edges_gdf, nodes_gdf = ox.graph_to_gdfs(graph)

    # Default styling
    edges_gdf["edge_colour"] = "#FFFFFF"
    edges_gdf["edge_alpha"] = 0.4
    nodes_gdf["node_colour"] = "#FFFFFF"
    nodes_gdf["node_size"] = 15
    nodes_gdf["node_alpha"] = 0.4

    # Set every edge in the shortest path to blue and fully visible
    for u, v in zip(node_path[:-1], node_path[1:]):
        edges_gdf.loc[(u, v), "edge_colour"] = "#0000FF"
        edges_gdf.loc[(u, v), "edge_alpha"] = 1

    # Find the first and last node in the path and make them red and easy to see
    start = node_path[0]
    end = node_path[-1]

    nodes_gdf.loc[start, ["node_colour", "node_size", "node_size", "node_alpha"]] = ["#FF0000", 35, 1]
    nodes_gdf.loc[end, ["node_colour", "node_size", "node_alpha"]] = ["#FF0000", 35, 1]

    # Recreate the route graph from the GDFs with the colour formatting included
    routeGraph = ox.graph_from_gdfs(nodes_gdf, edges_gdf)

    # Set lists for the colours, alphas and sizes of each edge in the graph
    edge_colours = [d.get("edge_colour") for _, _, _, d in routeGraph.edges(keys=True, data=True)]
    edge_alphas = [d.get("edge_alpha") for _, _, _, d in routeGraph.edges(keys=True, data=True)]
    node_colours = [d.get("node_colour") for _, d in routeGraph.nodes(data=True)]
    node_sizes = [d.get("node_size") for _, d in routeGraph.nodes(data=True)]
    node_alphas = [d.get("node_alpha") for _, d in routeGraph.nodes(data=True)]

    # Create the plot with the correct colouring
    fig, ax = ox.plot_graph(
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
    fig.savefig(savingFilePath, dpi=300)

def plot_crime_graph(graph : nx.MultiDiGraph, 
                     filePath : str = "graphs/png/crime_graph.png"):
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

def plot_blank_graph(coords : tuple, 
                     radius : int, 
                     travel_type : str, 
                     saveToFile : bool = False, 
                     filePath : str = "graphs/png/blank_graph.png"):
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

def plot_filled_graph(features : list, 
                      coords : tuple, 
                      radius : int, 
                      travel_type : str, 
                      saveToFile : bool = False, 
                      incLegend : bool = False, 
                      filePath : str = f"mapping/graphs/filled_graph.png"):
    
    graph = plot_blank_graph(coords, radius, travel_type)
    fig, ax = get_figure_and_axes(graph)
    
    for feature in features:
        add_feature_to_graph(graph, ax, coords, feature)
    
    if(incLegend):
        ax.legend()

    if(saveToFile):
        fig.savefig(filePath, dpi=300)

    return graph

def get_figure_and_axes(graph : nx.MultiDiGraph):
    return ox.plot_graph(graph, show=False, close=False)