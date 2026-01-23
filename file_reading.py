import pandas as pd

def edge_csv_to_dict(filepath : str) -> dict:
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