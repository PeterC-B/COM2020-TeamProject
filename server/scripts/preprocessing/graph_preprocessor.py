"""
Graph Preprocessor (Developer Use Only)
---------------------------------------

This script fetches a walking network from OSMnx, attaches Healthy Streets
indicators, normalises attributes, and saves a processed NetworkX MultiDiGraph
to disk.

This file is NOT used by the Flask backend at runtime.
The backend loads the preprocessed graph from disk.

Outputs:
    - processed_graph.pkl (primary runtime graph)
    - processed_graph.graphml (optional)
    - nodes_table.csv
    - edges_table.csv
"""

import os
import pickle
import osmnx as ox
import networkx as nx
import pandas as pd

from server.app.domain.indicators.attribute_extraction import (
    attach_edge_indicators,
    compute_amenity_proximity,
)
from server.app.domain.indicators.normalisation import normalise_graph_attributes


# ---------------------------------------------------------
# Output paths
# ---------------------------------------------------------

OUTPUT_DIR = "server/data/processed"
GRAPH_PKL = os.path.join(OUTPUT_DIR, "processed_graph.pkl")
GRAPH_GRAPHML = os.path.join(OUTPUT_DIR, "processed_graph.graphml")
NODES_CSV = os.path.join(OUTPUT_DIR, "nodes_table.csv")
EDGES_CSV = os.path.join(OUTPUT_DIR, "edges_table.csv")


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def fetch_graph(place_name: str) -> nx.MultiDiGraph:
    print(f"[1] Fetching walking network for: {place_name}")
    # OSMnx already returns a simplified graph by default
    graph = ox.graph_from_place(place_name, network_type="walk")
    return graph


def simplify_graph(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Previously attempted to simplify manually.
    OSMnx already simplifies graphs automatically,
    so this is now a no-op.
    """
    print("[2] Skipping simplification (OSMnx already simplified)")
    return graph


def extract_indicators(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    print("[3] Attaching Healthy Streets indicators...")
    return attach_edge_indicators(graph)


def normalise_indicators(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    print("[4] Normalising indicator values...")
    return normalise_graph_attributes(graph)


def save_graph(graph: nx.MultiDiGraph):
    print("[5] Saving processed graph...")

    # Save pickle (primary runtime format)
    with open(GRAPH_PKL, "wb") as f:
        pickle.dump(graph, f)

    # Save GraphML (optional, useful for debugging)
    ox.save_graphml(graph, GRAPH_GRAPHML)

    # Save node/edge tables for analytics
    nodes, edges = ox.graph_to_gdfs(graph)
    nodes.to_csv(NODES_CSV, index=False)
    edges.to_csv(EDGES_CSV, index=False)

    print("Saved:")
    print(f"  - {GRAPH_PKL}")
    print(f"  - {GRAPH_GRAPHML}")
    print(f"  - {NODES_CSV}")
    print(f"  - {EDGES_CSV}")


# ---------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------

def build_processed_graph(place_name: str):
    """
    Full preprocessing pipeline.
    Run this once during development to generate the seeded dataset.
    """

    ensure_output_dir()

    print("=== Building Processed Graph ===")

    # Used for amenity proximity calculations
    center_coords = ox.geocode(place_name)

    graph = fetch_graph(place_name)
    graph = simplify_graph(graph)  # now a no-op
    graph = extract_indicators(graph)
    graph = compute_amenity_proximity(graph, center_coords)  # optional
    graph = normalise_indicators(graph)
    save_graph(graph)

    print("=== Preprocessing Complete ===")
    return graph


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    build_processed_graph("Bristol, UK")