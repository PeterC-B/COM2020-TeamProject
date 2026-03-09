"""
Graph Cache
-----------

Caches the fully processed routing graph (NetworkX MultiDiGraph)
to avoid expensive reloads during runtime.

This cache is used by graph_loader.py, not by the preprocessor.
"""

import os
import pickle
import networkx as nx


CACHE_PATH = "data/routing_graph_cache.pkl"
CACHE_VERSION = "v2"   # bump this if indicators or scoring change


def cache_exists() -> bool:
    """Return True if a cached graph file exists."""
    return os.path.exists(CACHE_PATH)


def load_cached_graph():
    """
    Load cached routing graph from disk.

    Returns:
        - NetworkX MultiDiGraph if cache is valid
        - None if cache missing or invalid
    """
    if not cache_exists():
        return None

    try:
        with open(CACHE_PATH, "rb") as f:
            payload = pickle.load(f)

        # Validate structure
        if payload.get("version") != CACHE_VERSION:
            return None

        graph = payload.get("graph")
        if not isinstance(graph, nx.MultiDiGraph):
            return None

        return graph

    except Exception as e:
        print(f"Failed to load cached graph: {e}")
        return None


def save_cached_graph(graph: nx.MultiDiGraph):
    """
    Save routing graph to disk.
    """
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

    try:
        payload = {
            "version": CACHE_VERSION,
            "graph": graph
        }

        with open(CACHE_PATH, "wb") as f:
            pickle.dump(payload, f)

        print("Routing graph saved to cache")

    except Exception as e:
        print(f"Failed to save cached graph: {e}")