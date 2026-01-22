"""
Graph cache:
    - Save processed graphs to disk
    - Load cached graphs to avoid reprocessing
    - Handle versioning if attributes change
"""
import os

cache_path = "data/processed_graph.pkl"#

# Load processed graph from disk if available
def load_cached_graph():
    pass

# Save processed graph from disk
def save_cached_graph(graph):
    pass

# Return true if a cached graph file exists
def cache_exists():
    pass
