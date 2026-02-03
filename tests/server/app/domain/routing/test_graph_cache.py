import pytest
import networkx as nx

from server.app.domain.routing.graph_cache import (
    cache_exists,
    load_cached_graph,
    save_cached_graph,
    CACHE_PATH,
    CACHE_VERSION,
)

def test_cache_exists_true(monkeypatch):
    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.os.path.exists",
        lambda path: True
    )
    assert cache_exists() is True

def test_cache_exists_false(monkeypatch):
    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.os.path.exists",
        lambda path: False
    )
    assert cache_exists() is False

def test_load_cached_graph_missing(monkeypatch):
    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.cache_exists",
        lambda: False
    )
    assert load_cached_graph() is None

def test_load_cached_graph_version_mismatch(monkeypatch):
    # Mock payload with wrong version
    payload = {"version": "old", "graph": nx.MultiDiGraph()}

    class DummyFile:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("builtins.open", lambda *a, **k: DummyFile())
    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.pickle.load",
        lambda f: payload
    )
    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.cache_exists",
        lambda: True
    )

    assert load_cached_graph() is None

def test_load_cached_graph_wrong_type(monkeypatch):
    payload = {"version": CACHE_VERSION, "graph": "not a graph"}

    class DummyFile:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("builtins.open", lambda *a, **k: DummyFile())
    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.pickle.load",
        lambda f: payload
    )
    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.cache_exists",
        lambda: True
    )

    assert load_cached_graph() is None

def test_load_cached_graph_success(monkeypatch):
    G = nx.MultiDiGraph()
    payload = {"version": CACHE_VERSION, "graph": G}

    class DummyFile:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("builtins.open", lambda *a, **k: DummyFile())
    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.pickle.load",
        lambda f: payload
    )
    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.cache_exists",
        lambda: True
    )

    assert load_cached_graph() is G

def test_load_cached_graph_pickle_error(monkeypatch):
    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.cache_exists",
        lambda: True
    )

    class DummyFile:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("builtins.open", lambda *a, **k: DummyFile())
    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.pickle.load",
        lambda f: (_ for _ in ()).throw(Exception("boom"))
    )

    assert load_cached_graph() is None

def test_save_cached_graph_success(monkeypatch):
    G = nx.MultiDiGraph()
    saved = {"called": False, "payload": None}

    # Mock directory creation
    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.os.makedirs",
        lambda *a, **k: None
    )

    # Mock pickle.dump
    def fake_dump(payload, file):
        saved["called"] = True
        saved["payload"] = payload

    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.pickle.dump",
        fake_dump
    )

    # Mock open
    class DummyFile:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("builtins.open", lambda *a, **k: DummyFile())

    save_cached_graph(G)

    assert saved["called"] is True
    assert saved["payload"]["version"] == CACHE_VERSION
    assert saved["payload"]["graph"] is G


def test_save_cached_graph_exception(monkeypatch):
    G = nx.MultiDiGraph()

    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.os.makedirs",
        lambda *a, **k: None
    )

    # Force pickle.dump to fail
    monkeypatch.setattr(
        "server.app.domain.routing.graph_cache.pickle.dump",
        lambda *a, **k: (_ for _ in ()).throw(Exception("boom"))
    )

    class DummyFile:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("builtins.open", lambda *a, **k: DummyFile())

    # Should not raise
    save_cached_graph(G)