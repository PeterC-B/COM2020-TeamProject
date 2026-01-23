import osmnx as ox

# Loads an OSMnx graph for the given place and returns a MultiDiGraph
def load_graph(place_name):
    graph = ox.graph_from_place(place_name, network_type="walk")
    return graph

def simplify_graph(graph):
    return ox.simplify_graph(graph)

# Extracts and normalises Healthy Streets attributes
def extract_edge_attributes(graph):
    for u, v, key, data in graph.edges(keys=True, data=True):
        data["distance"] = data.get("length", 1)
        data["lighting"] = 0.5
        data["greenery"] = 0.5
        data["pollution"] = 0.5
    return graph

"""def extract_edge_attributes(graph):
    for u, v, key, data in graph.edges(keys=True, data=True):

        # Distance (OSMnx gives this automatically)
        data["distance"] = data.get("length", 1)

        # Lighting
        lit_tag = data.get("lit")
        data["lighting"] = 1.0 if lit_tag == "yes" else 0.0

        # Greenery (example: distance to nearest tree)
        data["greenery"] = compute_greenery_score(u, v, graph)

        # Pollution proxy (example: road type)
        data["pollution"] = pollution_from_highway_type(data.get("highway"))

        # Surface quality
        data["surface_quality"] = surface_score(data.get("surface"))

    return graph"""

"""
High-level function that:
    Loads the graph
    Simplifies it
    Extracts/normalises attributes
    Converts to a simple adjacency dict for algorithms
"""
def build_routing_graph(place_name):
    graph = load_graph(place_name)
    graph = simplify_graph(graph)
    graph = extract_edge_attributes(graph)

    # Convert to adjacency dict
    routing_graph = convert_to_algorithm_graph(graph)
    return routing_graph

"""
Converts OSMnx MultiDiGraph into:
    {node: {neighbour: {attribute: value}}}
"""
def convert_to_algorithm_graph(osmnx_graph):
    routing_graph = {}

    for u, v, data in osmnx_graph.edges(data=True):
        if u not in routing_graph:
            routing_graph[u] = {}
        routing_graph[u][v] = {
            "distance": data.get("distance", 1),
            "lighting": data.get("lighting", 0.5),
            "greenery": data.get("greenery", 0.5),
            "pollution": data.get("pollution", 0.5)
        }
    return routing_graph