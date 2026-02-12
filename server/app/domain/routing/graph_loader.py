"""
Graph Loader (Runtime)
----------------------

Loads the preprocessed NetworkX MultiDiGraph created by
graph_preprocessor.py. This loader is used by the Flask backend
at runtime and performs no OSMnx calls.

Responsibilities:
    - Load processed_graph.pkl
    - Validate graph structure
    - Ensure indicators exist
    - Ensure normalisation exists
    - Optionally cache the loaded graph in memory
"""

import os
import pickle
import networkx as nx

from app.domain.routing.graph_cache import load_cached_graph, save_cached_graph
from app.domain.indicators.attribute_extraction import attach_edge_indicators
from app.domain.indicators.normalisation import normalise_graph_attributes


PROCESSED_GRAPH_PATH = "server/data/processed/processed_graph.pkl"


def load_graph_from_disk() -> nx.MultiDiGraph:
    """Load the preprocessed graph from disk."""
    if not os.path.exists(PROCESSED_GRAPH_PATH):
        raise FileNotFoundError(
            f"Processed graph not found at {PROCESSED_GRAPH_PATH}. "
            "Run graph_preprocessor.py first to generate the seeded dataset."
        )

    with open(PROCESSED_GRAPH_PATH, "rb") as f:
        graph = pickle.load(f)

    if not isinstance(graph, nx.MultiDiGraph):
        raise TypeError("Loaded graph is not a NetworkX MultiDiGraph")

    return graph


def ensure_indicators(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Ensure indicator attributes exist on edges.
    If the preprocessed graph already contains them, this is a no-op.
    """
    sample_u, sample_v, sample_k, sample_data = next(iter(graph.edges(keys=True, data=True)))

    required = {"lighting", "greenery", "pollution", "surface_quality", "amenity_proximity"}

    if required.issubset(sample_data.keys()):
        return graph  # already processed

    return attach_edge_indicators(graph)


def ensure_normalisation(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Ensure indicator values are normalised.
    If already normalised, this is a no-op.
    """
    sample_u, sample_v, sample_k, sample_data = next(iter(graph.edges(keys=True, data=True)))

    if sample_data.get("lighting", None) is not None and 0 <= sample_data["lighting"] <= 1:
        return graph  # assume normalised

    return normalise_graph_attributes(graph)


def build_routing_graph(use_cache=True) -> nx.MultiDiGraph:
    """
    High-level runtime loader:
        - Load cached graph if available
        - Otherwise load from disk
        - Ensure indicators exist
        - Ensure normalisation exists
        - Cache final graph
    """

    if use_cache:
        cached = load_cached_graph()
        if cached is not None:
            print("Loaded routing graph from cache")
            return cached

    print("Loading processed graph from disk...")
    graph = load_graph_from_disk()

    graph = ensure_indicators(graph)
    graph = ensure_normalisation(graph)

    if use_cache:
        save_cached_graph(graph)
        print("Routing graph cached for future use")

    return graph

if __name__ == "__main__":
    print("Loading graph...")
    graph = load_graph_from_disk()
    print("Adding indicators...")
    graph = ensure_indicators(graph)
    print("Ensuring normalisation...")
    graph = ensure_normalisation(graph)
    print("Saving cached graph...")
    save_cached_graph(graph)
    print("Complete...")