"""
Graph Conversion:
    - Convert OSMnx MultiDiGraph into a simple adjacency dict:
        {node: {neighbour: {attribute: value}}}
    - Extract node coordinates for geometry utilities
"""

# Convert OSMnx grpah into adjacency dict for routing algorithms
def convert_to_algorithm_graph(osmnx_graph):
    pass

# Return a dict mapping node_id -> (lat, lon)
# Useful for geometry_utils
def extract_node_coordinates(osmnx_graph):
    pass