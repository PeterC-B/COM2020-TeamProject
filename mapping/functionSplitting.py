import osmnx as ox
import geopandas as gpd
import networkx as nx
import pandas as pd

def addDistanceToDrinkingPlace(edges_gdf : gpd.GeoDataFrame, coords : tuple) -> gpd.GeoDataFrame:
    '''
    A function that returns a heatmap of where roads are close to places that allow people to drink
    
    :param edges_gdf: The GeoDataFrame that contains the edges in the chosen map
    :type edges_gdf: gpd.GeoDataFrame
    :param coords: The centre coordinates for the chosen area
    :type coords: tuple
    :return: The graph where edges are coloured based on their proximity to a place of drink
    :rtype: GeoDataFrame
    '''
    amenities = ox.features_from_point(
        coords,
        tags={"amenity":[
                "bar", "biergarten", "pub", "casino", "nightclub", "gambling"
            ]},
        dist=450,
    )

    edges_m = edges_gdf.to_crs(epsg=27700)
    amenities_m = amenities.to_crs(epsg=27700)

    nearest = gpd.sjoin_nearest(
        edges_m,
        amenities_m,
        how="left",
        distance_col="dist_to_amenity",
    )

    def distance_score(d):
        if d is None or d > 1000:
            return 0
        return 1 / (d+1)
    
    nearest["access_score"] = nearest["dist_to_amenity"].apply(distance_score)
    edges_gdf["access_score"] = nearest["access_score"].values

    return edges_gdf

def addFeatureToGraph(graph : nx.MultiDiGraph, line, coords : tuple, feature : list, limit_amenities : bool = True) -> gpd.GeoDataFrame:
    '''
    Adds all features given to a graph of an area
    
    :param graph: The graph of the chosen area that has been generated
    :type graph: nx.MultiDiGraph
    :param line: The figure already generated
    :param coords: A tuple of the coordinates on Earth that the area is centered around
    :type coords: tuple
    :param feature: The list of features that you want to add to the graph
    :type feature: list
    :param limit_amenities: Are we limiting the amount of POIs to 80?
    :type limit_amenities: bool
    :return: The update GDF of the graph
    :rtype: gpd.GeoDataFrame
    '''
    features = ox.features_from_point(
        center_point=coords,
        tags=feature[1],
        dist=450,
    )

    if feature[0] == "Amenities" and limit_amenities == True:
        print("Old Amenities:", len(features))
        if len(features) >= 80:
            features = features.sample(n=80, random_state=42)
        else:
            features = features.copy()
        print("New Amenities:", len(features))


    features["centroid"] = features.geometry.centroid

    features["nearest_node"] = ox.distance.nearest_nodes(
        graph,
        X=features.centroid.x,
        Y=features.centroid.y
    )

    features.plot(
        ax=line,
        color=feature[2],
        label=feature[0],
        alpha=feature[3],
        markersize=feature[4],
    )

def csv_to_dict(filepath : str) -> dict:
    '''
    Converts the edges csv file into dictionary with all connections
    
    :param filepath: The filepath of the csv file that contains all info on every edge in the graph
    :type filepath: str
    :return: A dictionary that contains the 'from_node' as it's keys, and each node this connects to, with the length
    :rtype: dict
    '''
    allEdges = {}
    csv = pd.read_csv(filepath)
    for index, row in csv.iterrows():
        if int(row["from_node"]) not in allEdges:
            allEdges[int(row["from_node"])] = {int(row["to_node"]) : float(row["length"])}
        else:
            allEdges[int(row["from_node"])][int(row["to_node"])] = float(row["length"])
    return allEdges

def node_csv_to_dict(filepath:str) -> dict:
    '''
    Converts a csv file containing every node's information into a dictionary to be read
    
    :param filepath: The filepath of the csv file that contains all info on every node in the graph 
    :type filepath: str
    :return: A dictionary that contains the 'node_id' as it's keys, and each nodes x and y coordinates as it's tuple value
    :rtype: dict
    '''
    allNodes = {}
    csv = pd.read_csv(filepath)
    for index, row in csv.iterrows():
        allNodes[int(row["node_id"])] = (float(row["x"]), float(row["y"]))
    return allNodes

def find_edge_path(nodePath: list, edgeTablePath : str) -> list:
    '''
    Converts the path of nodes that a route follows into a path of the edges it follows
    
    :param nodePath: A path of nodes that a route follows
    :type nodePath: list
    :param edgeTablePath: The filepath for the csv file that contains all edge information
    :type edgeTablePath: str
    :return: A list containing a path of edges that the route follows in a readable format
    :rtype: list
    '''
    edgeCSV = pd.read_csv(edgeTablePath)
    pathLength = len(nodePath)
    i = 0
    edgePath = []
    while i < pathLength - 1:
        row = edgeCSV[(edgeCSV["from_node"] == nodePath[i]) & (edgeCSV["to_node"] == nodePath[i+1])]
        edgePath.append(int(row["edge_id"].iloc[0]))
        i += 1
    return edgePath

def edge_path_to_csv_rule(nodePath : list, edgeTablePath : str) -> list:
    '''
    Converts the path of nodes into the path of edges in the shortest route. Returns it in a way that can be queried with the CSV file

    :param nodePath: A path of nodes that a route follows
    :type nodePath: list
    :param edgeTablePath: The filepath for the csv file that contains all edge information
    :type edgeTablePath: str
    :return: A list containing a path of edges that the route follows in the format that the csv file can be queried with
    :rtype: list
    '''
    edgeCSV = pd.read_csv(edgeTablePath)
    edgePath = find_edge_path(nodePath, edgeTablePath)
    tuplePath = []
    pathLength = len(edgePath)
    i = 0
    while i < pathLength:
        row = edgeCSV[edgeCSV["edge_id"] == edgePath[i]]
        tuplePath.append((int(row["from_node"]), int(row["to_node"]), int(row["key"])))
        i += 1
    return tuplePath

def calculate_distance_from_node_path(nodePath : list, edgeTablePath : str) -> float:
    edgePath = find_edge_path(nodePath, edgeTablePath)
    edgeCSV = pd.read_csv(edgeTablePath)
    distance = 0
    for edge in edgePath:
        distance += float(edgeCSV[edgeCSV["edge_id"] == edge]["length"].iloc[0])
    return distance

if __name__ == "__main__":
    nodePath = [104804, 282237615, 19875363, 5906108608, 19875366, 104837, 5906030287, 262442708, 104838, 287226483, 3332266263, 287226495, 3696173720, 9464338656, 644926923, 5823455892, 3329881929, 6937982874, 1280853173, 1382252976, 247834407, 242756955, 17406787, 104859, 365559371, 13288882110]
    print(f"Edge path: {find_edge_path(nodePath, "edges_table.csv")}")
    #print(f"Edge path (u, v, key): {edge_path_to_csv_rule(nodePath, "edges_table.csv")}")