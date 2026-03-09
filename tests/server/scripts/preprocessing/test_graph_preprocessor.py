import pytest
import networkx as nx
import pandas as pd
import geopandas as gpd

from tests.utils.graph_preprocessor_core import (
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
import tests.utils.graph_preprocessor_core as gp


def test_ensure_output_dir(monkeypatch):
    calls = {"mkdir": False}

    monkeypatch.setattr(gp.os.path, "exists", lambda path: False)
    monkeypatch.setattr(gp.os, "makedirs", lambda path: calls.update({"mkdir": True}))

    ensure_output_dir()
    assert calls["mkdir"] is True


def test_fetch_graph(monkeypatch):
    fake_graph = nx.MultiDiGraph()

    def fake_graph_from_place(place, network_type):
        assert place == "Test City"
        assert network_type == "walk"
        return fake_graph

    monkeypatch.setattr(gp.ox, "graph_from_place", fake_graph_from_place)

    out = fetch_graph("Test City")
    assert out is fake_graph


def test_simplify_graph_noop():
    G = nx.MultiDiGraph()
    assert simplify_graph(G) is G


def test_extract_indicators(monkeypatch):
    G = nx.MultiDiGraph()
    G2 = nx.MultiDiGraph()

    monkeypatch.setattr(gp, "attach_edge_indicators", lambda graph: G2)

    out = extract_indicators(G)
    assert out is G2


def test_normalise_indicators(monkeypatch):
    G = nx.MultiDiGraph()
    G2 = nx.MultiDiGraph()

    monkeypatch.setattr(gp, "normalise_graph_attributes", lambda graph: G2)

    out = normalise_indicators(G)
    assert out is G2


def test_save_graph(monkeypatch):
    G = nx.MultiDiGraph()

    calls = {"pickle": False, "graphml": False, "nodes": False, "edges": False}

    # Mock pickle.dump
    monkeypatch.setattr(gp.pickle, "dump", lambda obj, file: calls.update({"pickle": True}))

    # Mock save_graphml
    def fake_save_graphml(graph, path):
        assert graph is G
        assert path == GRAPH_GRAPHML
        calls["graphml"] = True

    monkeypatch.setattr(gp.ox, "save_graphml", fake_save_graphml)

    # Mock graph_to_gdfs
    fake_nodes = gpd.GeoDataFrame({"x": [1]})
    fake_edges = gpd.GeoDataFrame({"y": [2]})

    monkeypatch.setattr(gp.ox, "graph_to_gdfs", lambda graph: (fake_nodes, fake_edges))

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

    monkeypatch.setattr(gp, "ensure_output_dir", lambda: None)
    monkeypatch.setattr(gp.ox, "geocode", lambda place: (51.0, -2.0))
    monkeypatch.setattr(gp, "fetch_graph", lambda place: G0)
    monkeypatch.setattr(gp, "simplify_graph", lambda g: G1)
    monkeypatch.setattr(gp, "extract_indicators", lambda g: G2)
    monkeypatch.setattr(gp, "compute_amenity_proximity", lambda g, coords: G3)
    monkeypatch.setattr(gp, "normalise_indicators", lambda g: G4)

    saved = {"called": False}
    monkeypatch.setattr(gp, "save_graph", lambda g: saved.update({"called": True}))

    out = build_processed_graph("Test City")

    assert out is G4
    assert saved["called"] is True
