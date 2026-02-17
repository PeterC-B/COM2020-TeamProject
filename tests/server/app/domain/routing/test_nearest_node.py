import pytest
import networkx as nx
from tests.load_module import load_module

from tests.utils.nearest_node_core import get_nearest_node

def test_nearest_node_basic():
    G = nx.MultiDiGraph()
    G.add_node(1, x=0.0, y=0.0)
    G.add_node(2, x=1.0, y=1.0)
    G.add_node(3, x=5.0, y=5.0)

    nearest = get_nearest_node(G, (0.2, 0.1))
    assert nearest == 1

def test_nearest_node_second_closest():
    G = nx.MultiDiGraph()
    G.add_node(10, x=10.0, y=10.0)
    G.add_node(20, x=0.0, y=0.0)

    nearest = get_nearest_node(G, (9.0, 9.0))
    assert nearest == 10

def test_nearest_node_skips_missing_coordinates():
    G = nx.MultiDiGraph()
    G.add_node(1, x=None, y=None)
    G.add_node(2, x=1.0, y=1.0)

    nearest = get_nearest_node(G, (1.1, 1.1))
    assert nearest == 2

def test_nearest_node_all_missing_coordinates():
    G = nx.MultiDiGraph()
    G.add_node(1, x=None, y=None)
    G.add_node(2, x=None, y=None)

    with pytest.raises(ValueError):
        get_nearest_node(G, (0.0, 0.0))

# Edge cases
def test_nearest_node_exact_match():
    G = nx.MultiDiGraph()
    G.add_node(1, x=3.0, y=4.0)
    G.add_node(2, x=10.0, y=10.0)

    nearest = get_nearest_node(G, (3.0, 4.0))
    assert nearest == 1

def test_nearest_node_tie_returns_first_encountered():
    G = nx.MultiDiGraph()
    # Both nodes are equidistant from (0,0)
    G.add_node(1, x=1.0, y=1.0)
    G.add_node(2, x=-1.0, y=-1.0)

    nearest = get_nearest_node(G, (0.0, 0.0))
    # Implementation picks the first one encountered
    assert nearest == 1


def test_nearest_node_negative_coordinates():
    G = nx.MultiDiGraph()
    G.add_node(1, x=-5.0, y=-5.0)
    G.add_node(2, x=5.0, y=5.0)

    nearest = get_nearest_node(G, (-4.9, -5.1))
    assert nearest == 1