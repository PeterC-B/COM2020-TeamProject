"""
Graph Conversion:
    - Convert OSMnx MultiDiGraph into a simple adjacency dict:
        {node: {neighbour: {attribute: value}}}
    - Extract node coordinates for geometry utilities
"""
import geopandas as gpd

def create_nodes_table(nodes_gdf : gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    '''
    Creates a readable table for the nodes GDF
    
    :param nodes_gdf: The GeoDataFrame containing all information on nodes
    :type nodes_gdf: gpd.GeoDataFrame
    :return: The created nodes table
    :rtype: GeoDataFrame
    '''
    nodes_table = nodes_gdf.reset_index()[["osmid", "x", "y"]]
    nodes_table = nodes_table.rename(columns={"osmid" : "node_id"})
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


def convert_to_algorithm_graph(osmnx_graph):
    """
    Convert OSMnx grpah into adjacency dict for routing algorithms
    
    Output format:
    {
        node_u: {
            node_v: {
                "distance":float,
                "lighting": float,
                "greenery": float,
                "pollution": float,
                "surface_quality": float
                },
                ...
            },
            ...
        }
    """
    routing_graph = {}

    for u, v, data in osmnx_graph.edges(data=True):

        # Ensure node exists in adjacency dict
        if u not in routing_graph:
            routing_graph[u] = {}
        
        # Extract attributes (with safe defaults)
        routing_graph[u][v] = {
            "distance": data.get("distance", data.get("length", 1)),
            "lighting": data.get("lighting", 0.0),
            "greenery": data.get("greenery", 0.0),
            "pollution": data.get("pollution", 0.0),
            "surface_quality": data.get("surface_quality", 0.5),
        }

    return routing_graph

def extract_node_coordinates(osmnx_graph):
    """
    Return a dict mapping node_id -> (lat, lon)

    Useful for:
        - converting node paths to coordinate paths
        - GeoJSON generation
        - frontend visualisation
    """

    coords = {}

    for node_id, data in osmnx_graph.nodes(data=True):
        lat = data.get("y")
        lon = data.get("x")

        if lat is not None and lon is not None:
            coords[node_id] = (lat, lon)

    return coords