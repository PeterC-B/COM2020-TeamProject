import pytest
import networkx as nx

from tests.utils.graph_cache_core import (
    cache_exists,
    load_cached_graph,
    save_cached_graph,
    CACHE_PATH,
    CACHE_VERSION,
)
import tests.utils.graph_cache_core as graph_cache


def test_cache_exists_true(monkeypatch):
    monkeypatch.setattr(graph_cache.os.path, "exists", lambda path: True)
    assert cache_exists() is True


def test_cache_exists_false(monkeypatch):
    monkeypatch.setattr(graph_cache.os.path, "exists", lambda path: False)
    assert cache_exists() is False


def test_load_cached_graph_missing(monkeypatch):
    monkeypatch.setattr(graph_cache, "cache_exists", lambda: False)
    assert load_cached_graph() is None


def test_load_cached_graph_version_mismatch(monkeypatch):
    payload = {"version": "old", "graph": nx.MultiDiGraph()}

    class DummyFile:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("builtins.open", lambda *a, **k: DummyFile())
    monkeypatch.setattr(graph_cache.pickle, "load", lambda f: payload)
    monkeypatch.setattr(graph_cache, "cache_exists", lambda: True)

    assert load_cached_graph() is None


def test_load_cached_graph_wrong_type(monkeypatch):
    payload = {"version": CACHE_VERSION, "graph": "not a graph"}

    class DummyFile:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("builtins.open", lambda *a, **k: DummyFile())
    monkeypatch.setattr(graph_cache.pickle, "load", lambda f: payload)
    monkeypatch.setattr(graph_cache, "cache_exists", lambda: True)

    assert load_cached_graph() is None


def test_load_cached_graph_success(monkeypatch):
    G = nx.MultiDiGraph()
    payload = {"version": CACHE_VERSION, "graph": G}

    class DummyFile:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("builtins.open", lambda *a, **k: DummyFile())
    monkeypatch.setattr(graph_cache.pickle, "load", lambda f: payload)
    monkeypatch.setattr(graph_cache, "cache_exists", lambda: True)

    assert load_cached_graph() is G


def test_load_cached_graph_pickle_error(monkeypatch):
    monkeypatch.setattr(graph_cache, "cache_exists", lambda: True)

    class DummyFile:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("builtins.open", lambda *a, **k: DummyFile())
    monkeypatch.setattr(
        graph_cache.pickle,
        "load",
        lambda f: (_ for _ in ()).throw(Exception("boom")),
    )

    assert load_cached_graph() is None


def test_save_cached_graph_success(monkeypatch):
    G = nx.MultiDiGraph()
    saved = {"called": False, "payload": None}

    monkeypatch.setattr(graph_cache.os, "makedirs", lambda *a, **k: None)

    def fake_dump(payload, file):
        saved["called"] = True
        saved["payload"] = payload

    monkeypatch.setattr(graph_cache.pickle, "dump", fake_dump)

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

    monkeypatch.setattr(graph_cache.os, "makedirs", lambda *a, **k: None)

    monkeypatch.setattr(
        graph_cache.pickle,
        "dump",
        lambda *a, **k: (_ for _ in ()).throw(Exception("boom")),
    )

    class DummyFile:
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("builtins.open", lambda *a, **k: DummyFile())

    # Should not raise
    save_cached_graph(G)
