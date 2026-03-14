import os
import pickle
import networkx as nx
import osmnx as ox


OUTPUT_DIR = "app/data/processed"
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
    return ox.graph_from_place(place_name, network_type="walk")


def simplify_graph(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    return graph


def extract_indicators(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    return attach_edge_indicators(graph)


def normalise_indicators(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    return normalise_graph_attributes(graph)


def save_graph(graph: nx.MultiDiGraph):
    with open(GRAPH_PKL, "wb") as f:
        pickle.dump(graph, f)

    ox.save_graphml(graph, GRAPH_GRAPHML)

    nodes, edges = ox.graph_to_gdfs(graph)
    nodes.to_csv(NODES_CSV, index=False)
    edges.to_csv(EDGES_CSV, index=False)


def build_processed_graph(place_name: str):
    ensure_output_dir()

    coords = ox.geocode(place_name)

    graph = fetch_graph(place_name)
    graph = simplify_graph(graph)
    graph = extract_indicators(graph)
    graph = compute_amenity_proximity(graph, coords)
    graph = normalise_indicators(graph)
    save_graph(graph)

    return graph


# ---------------------------------------------------------
# Monkeypatch targets (stubs)
# ---------------------------------------------------------

def attach_edge_indicators(graph):
    raise NotImplementedError

def normalise_graph_attributes(graph):
    raise NotImplementedError

def compute_amenity_proximity(graph, coords):
    raise NotImplementedError
