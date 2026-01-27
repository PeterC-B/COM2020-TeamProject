"""
Graph cache:
    - Save processed graphs to disk
    - Load cached graphs to avoid reprocessing
    - Handle versioning if attributes change
"""
import os
import pickle

cache_path = "data/processed_graph.pkl"

# Return true if a cached graph file exists
def cache_exists():
    return os.path.exists(cache_path)

def load_cached_graph() -> bool:
    """
    Load processed graph from disk if available
    Returns:
        - the cached graph (adjacency dict)
        - None if no cache exists or loading fails
    """
    if not cache_exists():
        return None
    
    try:
        with open(cache_path, "rb") as f:
            graph = pickle.load(f)
        return graph
    except Exception as e:
        print(f"Failed to load cached graph: {e}")
        return None

# Save processed graph from disk
def save_cached_graph(graph):
    # Ensure directiory exists
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    try:
        with open(cache_path, "wb") as f:
            pickle.dump(graph, f)
        print("Processed graph saved to cache")
    except Exception as e:
        print(f"Failed to save cached graph: {e}")


