"""
File Reading Utilities:
    - Load edge lists from CSV
    - Load node coordinate lists from CSV
    - Convert node paths to edge paths using CSV tables
    - Compute distance from CSV-based graphs

These functions are useful for:
    - Testing algorithms without OSMnx
    - Loading custom graph datasets

"""
import pandas as pd

def edge_csv_to_dict(filepath : str) -> dict:
    '''
    Convert an edges CSV file into an adjacency dictionary

    Expected CSV columns:
        - from_node
        - to_node
        - length

    Returns:
        {
            from_node: {to_node: length,...
            },
            ...
        }
    '''
    allEdges = {}
    csv = pd.read_csv(filepath)

    for _, row in csv.iterrows():
        u = int(row["from_node"])
        v = int(row["to_node"])
        length = float(row["length"])

        if u not in allEdges:
            allEdges[u] = {}
        
        allEdges[u][v] = length
    return allEdges

def node_csv_to_dict(filepath:str) -> dict:
    '''
    Converts a nodes CSV file into a dictionary mapping node_id -> (x, y)

    Expected CSV columns:
        - node_id
        - x
        - y

    Returns:
    {
        node_id: (x, y),
        ...
    }
    '''
    allNodes = {}
    csv = pd.read_csv(filepath)

    for _, row in csv.iterrows():
        node_id = int(row["node_id"])
        coords = (float(row["x"]), float(row["y"]))
        allNodes[node_id] = coords
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
    edgePath = []

    for i in range(len(nodePath) - 1):
        u = nodePath[i]
        v = nodePath[i + 1]

        row = edgeCSV[(edgeCSV["from_node"] == u) &
                      (edgeCSV["to_node"] == v)]
        
        if row.empty:
            raise ValueError(f"No edge found for ({u} -> {v})")
        edgePath.append(int(row["edge_id"].iloc[0]))
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
    edge_ids = find_edge_path(nodePath, edgeTablePath)

    tuplePath = []

    for edge_id in edge_ids:
        row = edgeCSV[edgeCSV["edge_id"] == edge_id]

        if row.empty:
            raise ValueError(f"No edge found for edge_id={edge_id}")
        
        u = int(row["from_node"].iloc[0])
        v = int(row["to_node"].iloc[0])
        k = int(row["key"].iloc[0])

        tuplePath.append((u, v, k))
    return tuplePath

def calculate_distance_from_node_path(nodePath: list, edgeTablePath: str) -> float:
    edgeCSV = pd.read_csv(edgeTablePath)
    edge_ids = find_edge_path(nodePath, edgeTablePath)
    
    distance = 0.0

    for edge_id in edge_ids:
        row = edgeCSV[edgeCSV["edge_id"] == edge_id]

        if row.empty:
            raise ValueError(f"No edge found for edge_id={edge_id}")
        
        distance += float(row["length"].iloc[0])
    return distance