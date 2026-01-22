"""
Graph Loader:
    - Loads OSMnx graph data
    - Simplifies the graph
    - Extracts Healthy Street attributes
    - Normalises attributes
    - Converts to algorithm-friendly adjacency dict
    - Handles caching via graph_cache
"""

from .attribute_extraction import extract_edge_attributes
from .graph_conversion import convert_to_algorithm_graph
from .graph_cache import load_cached_graph, save_cached_graph

import osmnx as ox

# Load a raw OSMnx graph for the given place
def load_raw_graph(place_name):
    pass

# Simplify the OSMnx graph (...maybe)
def simplify_graph(graph):
    pass

# Apply attribute extraction and normalisation
# Returns a processed OSMnx graph
def preprocess_graph(graph):
    pass


def build_routing_graph(place_name, use_cache=True):
    """
    High-level function:
        - Load cached graph if available
        - Otherwise load raw graph
        - Simplify
        - Extract attributes
        - Convert to adjacency dict
        - Cache processed graph
    """
    pass
