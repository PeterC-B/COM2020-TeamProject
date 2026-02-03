import networkx as nx
from server.app.domain.routing.geometry_utils import extract_node_coordinates

def test_extract_node_coordinates_basic():
    G = nx.MultiDiGraph()
    G.add_node(1, x=-2.6, y=51.5)
    G.add_node(2, x=-2.7, y=51.6)

    coords = extract_node_coordinates(G)

    assert coords == {
        1: (51.5, -2.6),
        2: (51.6, -2.7),
    }

def test_extract_node_coordinates_missing_values():
    G = nx.MultiDiGraph()
    G.add_node(1, x=-2.6, y=51.5)
    G.add_node(2, x=None, y=51.6)   # missing lon
    G.add_node(3, x=-2.7, y=None)   # missing lat
    G.add_node(4)                   # no coords at all

    coords = extract_node_coordinates(G)

    assert coords == {
        1: (51.5, -2.6)
    }

def test_extract_node_coordinates_empty_graph():
    G = nx.MultiDiGraph()
    coords = extract_node_coordinates(G)
    assert coords == {}

def test_extract_node_coordinates_negative_values():
    G = nx.MultiDiGraph()
    G.add_node(1, x=-3.0, y=-10.0)

    coords = extract_node_coordinates(G)

    assert coords == {1: (-10.0, -3.0)}

def test_extract_node_coordinates_mixed_types():
    G = nx.MultiDiGraph()
    G.add_node(1, x="-2.6", y="51.5")  # strings but valid

    coords = extract_node_coordinates(G)

    # Function does not cast to float; it preserves raw values
    assert coords == {1: ("51.5", "-2.6")}