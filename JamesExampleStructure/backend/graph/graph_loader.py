"""
Graph Loader:
    - Loads OSMnx graph data
    - Simplifies the graph
    - Extracts Healthy Street attributes
    - Normalises attributes
    - Converts to algorithm-friendly adjacency dict
    - Handles caching via graph_cache
"""
import osmnx as ox
import networkx as nx

from .attribute_extraction import extract_edge_attributes
from .graph_conversion import convert_to_algorithm_graph
from .graph_cache import load_cached_graph, save_cached_graph


def create_graphml(graph : nx.MultiDiGraph, filepath="graph.graphml"):
    ox.save_graphml(graph, filepath)

# Load a raw OSMnx graph for the given place
def load_raw_graph(place_name: str) -> nx.MultiDiGraph:
    print(f"Loading raw graph for: {place_name}")
    graph = ox.graph_from_place(place_name, network_type="walk")
    return graph

# Simplify the OSMnx graph (remove unnecessary nodes, merge edges)
def simplify_graph(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    print("Simplifying graph... ")
    return ox.simplify_graph(graph)

# Apply HS attribute extraction to each edge
def preprocess_graph(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    print("Extracting attributes... ")
    return graph


def build_routing_graph(place_name: str, use_cache=True):
    """
    High-level function:
        - Load cached graph if available
        - Otherwise load raw graph
        - Simplify
        - Extract attributes
        - Convert to adjacency dict
        - Cache processed graph
    """

    # Try loading from cache
    if use_cache:
        cached = load_cached_graph()
        if cached is not None:
            print("Loaded graph from cache")
            return cached
    
    # Otherwise build from scratch

    print("""No cached graph found. 
          Building new graph... """)
    
    graph = load_raw_graph(place_name)
    graph = simplify_graph(graph)
    graph = preprocess_graph(graph)

    # Convert to adjacency dict for algorithms
    routing_graph = convert_to_algorithm_graph(graph)

    # Save to cache
    if use_cache:
        save_cached_graph(routing_graph)
        print("Graph cached for future use")
    
    return routing_graph


