import pytest
import networkx as nx

from server.app.domain.routing.graph_loader import (
    load_graph_from_disk,
    ensure_indicators,
    ensure_normalisation,
    build_routing_graph,
    PROCESSED_GRAPH_PATH,
)

def test_load_graph_from_disk_success(monkeypatch):
    G = nx.MultiDiGraph()

    # Mock filesystem
    monkeypatch.setattr(
        "server.app.domain.routing.graph_loader.os.path.exists",
        lambda path: True
    )

    # Mock pickle.load
    class DummyFile:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("builtins.open", lambda *a, **k: DummyFile())
    monkeypatch.setattr(
        "server.app.domain.routing.graph_loader.pickle.load",
        lambda f: G
    )

    out = load_graph_from_disk()
    assert out is G

def test_load_graph_from_disk_missing(monkeypatch):
    monkeypatch.setattr(
        "server.app.domain.routing.graph_loader.os.path.exists",
        lambda path: False
    )

    with pytest.raises(FileNotFoundError):
        load_graph_from_disk()

def test_load_graph_from_disk_wrong_type(monkeypatch):
    monkeypatch.setattr(
        "server.app.domain.routing.graph_loader.os.path.exists",
        lambda path: True
    )

    class DummyFile:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("builtins.open", lambda *a, **k: DummyFile())
    monkeypatch.setattr(
        "server.app.domain.routing.graph_loader.pickle.load",
        lambda f: "not a graph"
    )

    with pytest.raises(TypeError):
        load_graph_from_disk()

def test_ensure_indicators_noop(monkeypatch):
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, lighting=1, greenery=1, pollution=1,
               surface_quality=1, amenity_proximity=1)

    out = ensure_indicators(G)
    assert out is G

def test_ensure_indicators_calls_attach(monkeypatch):
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, foo=123)

    G2 = nx.MultiDiGraph()

    def fake_attach(graph):
        assert graph is G
        return G2

    monkeypatch.setattr(
        "server.app.domain.routing.graph_loader.attach_edge_indicators",
        fake_attach
    )

    out = ensure_indicators(G)
    assert out is G2

def test_ensure_normalisation_noop(monkeypatch):
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, lighting=0.5)  # already normalised

    out = ensure_normalisation(G)
    assert out is G

def test_ensure_normalisation_calls_normalise(monkeypatch):
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, lighting=5)  # not normalised

    G2 = nx.MultiDiGraph()

    def fake_norm(graph):
        assert graph is G
        return G2

    monkeypatch.setattr(
        "server.app.domain.routing.graph_loader.normalise_graph_attributes",
        fake_norm
    )

    out = ensure_normalisation(G)
    assert out is G2

def test_build_routing_graph_uses_cache(monkeypatch):
    G_cached = nx.MultiDiGraph()

    monkeypatch.setattr(
        "server.app.domain.routing.graph_loader.load_cached_graph",
        lambda: G_cached
    )

    out = build_routing_graph(use_cache=True)
    assert out is G_cached

def test_build_routing_graph_full_pipeline(monkeypatch):
    G0 = nx.MultiDiGraph()
    G1 = nx.MultiDiGraph()
    G2 = nx.MultiDiGraph()
    G3 = nx.MultiDiGraph()

    # No cache
    monkeypatch.setattr(
        "server.app.domain.routing.graph_loader.load_cached_graph",
        lambda: None
    )

    # load_graph_from_disk
    monkeypatch.setattr(
        "server.app.domain.routing.graph_loader.load_graph_from_disk",
        lambda: G0
    )

    # ensure_indicators
    monkeypatch.setattr(
        "server.app.domain.routing.graph_loader.ensure_indicators",
        lambda g: G1
    )

    # ensure_normalisation
    monkeypatch.setattr(
        "server.app.domain.routing.graph_loader.ensure_normalisation",
        lambda g: G2
    )

    # save_cached_graph
    saved = {"called": False}
    monkeypatch.setattr(
        "server.app.domain.routing.graph_loader.save_cached_graph",
        lambda g: saved.update({"called": True})
    )

    out = build_routing_graph(use_cache=True)

    assert out is G2
    assert saved["called"] is True