import pytest
import networkx as nx

from server.app.domain.indicators.normalisation import (
    normalise_value,
    normalise_edge_attributes,
    normalise_graph_attributes,
)

def test_normalise_value_basic():
    assert normalise_value(0.5) == 0.5
    assert normalise_value(1.0) == 1.0
    assert normalise_value(0.0) == 0.0

def test_normalise_value_none():
    assert normalise_value(None) == 0.5

def test_normalise_value_invalid_type():
    assert normalise_value("abc") == 0.5

def test_normalise_value_min_equals_max():
    assert normalise_value(10, min_val=5, max_val=5) == 0.5

def test_normalise_value_custom_range():
    # (value - 10) / (20 - 10) = 0.5
    assert normalise_value(15, min_val=10, max_val=20) == 0.5

def test_normalise_edge_attributes_basic():
    schema = {
        "lighting": {"default": 0.0, "normalise": True},
        "greenery": {"default": 0.0, "normalise": True},
        "pollution": {"default": 1.0, "normalise": False},
    }

    edge = {"lighting": 0.8, "greenery": 0.4, "pollution": 0.7}

    out = normalise_edge_attributes(edge, schema)

    assert out["lighting"] == 0.8
    assert out["greenery"] == 0.4
    assert out["pollution"] == 0.7  # not normalised

def test_normalise_edge_attributes_missing_values():
    schema = {
        "lighting": {"default": 0.2, "normalise": True},
        "greenery": {"default": 0.3, "normalise": True},
    }

    edge = {}  # missing both attributes

    out = normalise_edge_attributes(edge, schema)

    assert out["lighting"] == 0.2
    assert out["greenery"] == 0.3

def test_normalise_edge_attributes_invalid_value():
    schema = {"lighting": {"default": 0.0, "normalise": True}}
    edge = {"lighting": "invalid"}

    out = normalise_edge_attributes(edge, schema)

    assert out["lighting"] == 0.5  # fallback from normalise_value

def test_normalise_graph_attributes_default_schema():
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, lighting=0.8, greenery=0.4, pollution=0.6, surface_quality=0.3, amenity_proximity=0.9)

    out = normalise_graph_attributes(G)

    for _, _, data in out.edges(data=True):
        assert 0 <= data["lighting"] <= 1
        assert 0 <= data["greenery"] <= 1
        assert 0 <= data["pollution"] <= 1
        assert 0 <= data["surface_quality"] <= 1
        assert 0 <= data["amenity_proximity"] <= 1

def test_normalise_graph_attributes_custom_schema():
    schema = {
        "lighting": {"default": 0.0, "normalise": True},
        "greenery": {"default": 0.0, "normalise": False},  # should NOT be normalised
    }

    G = nx.MultiDiGraph()
    G.add_edge(1, 2, lighting=0.8, greenery=0.4)

    out = normalise_graph_attributes(G, schema=schema)

    for _, _, data in out.edges(data=True):
        assert data["lighting"] == 0.8
        assert data["greenery"] == 0.4  # unchanged