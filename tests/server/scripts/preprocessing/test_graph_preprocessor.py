import pytest
import networkx as nx
import pandas as pd
import geopandas as gpd

from server.scripts.preprocessing.graph_preprocessor import (
    build_processed_graph,
    ensure_output_dir,
    fetch_graph,
    simplify_graph,
    extract_indicators,
    normalise_indicators,
    save_graph,
    OUTPUT_DIR,
    GRAPH_PKL,
    GRAPH_GRAPHML,
    NODES_CSV,
    EDGES_CSV,
)

def test_ensure_output_dir(monkeypatch):
    calls = {"mkdir": False}

    def fake_exists(path):
        return False

    def fake_makedirs(path):
        calls["mkdir"] = True

    monkeypatch.setattr("server.scripts.preprocessing.graph_preprocessor.os.path.exists", fake_exists)
    monkeypatch.setattr("server.scripts.preprocessing.graph_preprocessor.os.makedirs", fake_makedirs)

    ensure_output_dir()
    assert calls["mkdir"] is True

def test_fetch_graph(monkeypatch):
    fake_graph = nx.MultiDiGraph()

    def fake_graph_from_place(place, network_type):
        assert place == "Test City"
        assert network_type == "walk"
        return fake_graph

    monkeypatch.setattr("server.scripts.preprocessing.graph_preprocessor.ox.graph_from_place", fake_graph_from_place)

    out = fetch_graph("Test City")
    assert out is fake_graph

def test_simplify_graph_noop():
    G = nx.MultiDiGraph()
    assert simplify_graph(G) is G

def test_extract_indicators(monkeypatch):
    G = nx.MultiDiGraph()
    G2 = nx.MultiDiGraph()

    def fake_attach(graph):
        assert graph is G
        return G2

    monkeypatch.setattr(
        "server.scripts.preprocessing.graph_preprocessor.attach_edge_indicators",
        fake_attach
    )

    out = extract_indicators(G)
    assert out is G2

def test_normalise_indicators(monkeypatch):
    G = nx.MultiDiGraph()
    G2 = nx.MultiDiGraph()

    def fake_norm(graph):
        assert graph is G
        return G2

    monkeypatch.setattr(
        "server.scripts.preprocessing.graph_preprocessor.normalise_graph_attributes",
        fake_norm
    )

    out = normalise_indicators(G)
    assert out is G2

def test_save_graph(monkeypatch):
    G = nx.MultiDiGraph()

    # Track calls
    calls = {"pickle": False, "graphml": False, "nodes": False, "edges": False}

    # Mock pickle.dump
    def fake_dump(obj, file):
        assert obj is G
        calls["pickle"] = True

    monkeypatch.setattr("server.scripts.preprocessing.graph_preprocessor.pickle.dump", fake_dump)

    # Mock save_graphml
    def fake_save_graphml(graph, path):
        assert graph is G
        assert path == GRAPH_GRAPHML
        calls["graphml"] = True

    monkeypatch.setattr("server.scripts.preprocessing.graph_preprocessor.ox.save_graphml", fake_save_graphml)

    # Mock graph_to_gdfs
    fake_nodes = gpd.GeoDataFrame({"x": [1]})
    fake_edges = gpd.GeoDataFrame({"y": [2]})

    def fake_to_gdfs(graph):
        assert graph is G
        return fake_nodes, fake_edges

    monkeypatch.setattr("server.scripts.preprocessing.graph_preprocessor.ox.graph_to_gdfs", fake_to_gdfs)

    # Mock to_csv
    def fake_to_csv(self, path, index=False):
        if path == NODES_CSV:
            calls["nodes"] = True
        elif path == EDGES_CSV:
            calls["edges"] = True

    monkeypatch.setattr(gpd.GeoDataFrame, "to_csv", fake_to_csv)

    # Mock open()
    class DummyFile:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: DummyFile())

    save_graph(G)

    assert all(calls.values())


def test_build_processed_graph(monkeypatch):
    G0 = nx.MultiDiGraph()
    G1 = nx.MultiDiGraph()
    G2 = nx.MultiDiGraph()
    G3 = nx.MultiDiGraph()
    G4 = nx.MultiDiGraph()

    # Mock ensure_output_dir
    monkeypatch.setattr(
        "server.scripts.preprocessing.graph_preprocessor.ensure_output_dir",
        lambda: None
    )

    # Mock geocode
    monkeypatch.setattr(
        "server.scripts.preprocessing.graph_preprocessor.ox.geocode",
        lambda place: (51.0, -2.0)
    )

    # Mock fetch_graph
    monkeypatch.setattr(
        "server.scripts.preprocessing.graph_preprocessor.fetch_graph",
        lambda place: G0
    )

    # Mock simplify_graph
    monkeypatch.setattr(
        "server.scripts.preprocessing.graph_preprocessor.simplify_graph",
        lambda g: G1
    )

    # Mock extract_indicators
    monkeypatch.setattr(
        "server.scripts.preprocessing.graph_preprocessor.extract_indicators",
        lambda g: G2
    )

    # Mock compute_amenity_proximity
    monkeypatch.setattr(
        "server.scripts.preprocessing.graph_preprocessor.compute_amenity_proximity",
        lambda g, coords: G3
    )

    # Mock normalise_indicators
    monkeypatch.setattr(
        "server.scripts.preprocessing.graph_preprocessor.normalise_indicators",
        lambda g: G4
    )

    # Mock save_graph
    saved = {"called": False}
    monkeypatch.setattr(
        "server.scripts.preprocessing.graph_preprocessor.save_graph",
        lambda g: saved.update({"called": True})
    )

    out = build_processed_graph("Test City")

    assert out is G4
    assert saved["called"] is True