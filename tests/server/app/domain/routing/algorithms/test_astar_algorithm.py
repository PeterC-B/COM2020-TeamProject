'''import pytest
import networkx as nx
from math import inf

from server.app.domain.routing.algorithms.astar_algorithm import astar

# Helpers
def unit_cost(edge_data):
    return 1

def length_cost(edge_data):
    return edge_data.get("length", 1)

def zero_heuristic(node):
    return 0

def simple_heuristic(node):
    # A fake heuristic that prefers higher-numbered nodes
    return -node

# Tests
def test_astar_simple_chain():
    """
    1 → 2 → 3 → 4
    All weights = 1
    """
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, length=1)
    G.add_edge(2, 3, length=1)
    G.add_edge(3, 4, length=1)

    dist, path = astar(G, 1, 4, length_cost, zero_heuristic, trace=False)

    assert dist == 3
    assert path == [1, 2, 3, 4]

def test_astar_branching_paths_with_heuristic():
    """
    Graph:
        1 → 2 → 4 (cost 10)
        1 → 3 → 4 (cost 2)
    Heuristic should not break correctness
    """
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, length=10)
    G.add_edge(2, 4, length=10)
    G.add_edge(1, 3, length=1)
    G.add_edge(3, 4, length=1)

    dist, path = astar(G, 1, 4, length_cost, zero_heuristic, trace=False)

    assert dist == 2
    assert path == [1, 3, 4]

def test_astar_no_path():
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, length=1)

    dist, path = astar(G, 1, 3, length_cost, zero_heuristic, trace=False)

    assert dist == inf
    assert path == []

def test_astar_source_equals_target():
    G = nx.MultiDiGraph()
    G.add_node(5)

    dist, path = astar(G, 5, 5, length_cost, zero_heuristic, trace=False)

    assert dist == 0
    assert path == [5]

def test_astar_multiedges():
    """
    MultiDiGraph:
        1 → 2 has two edges:
            - length 10
            - length 1
        2 → 3 length 1
    A* should choose the cheaper parallel edge
    """
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, length=10)
    G.add_edge(1, 2, length=1)
    G.add_edge(2, 3, length=1)

    dist, path = astar(G, 1, 3, length_cost, zero_heuristic, trace=False)

    assert dist == 2
    assert path == [1, 2, 3]

def test_astar_cycle_handling():
    """
    Graph with a cycle:
        1 → 2 → 3 → 1
        2 → 4
    Shortest path to 4 is 1→2→4
    """
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, length=1)
    G.add_edge(2, 3, length=1)
    G.add_edge(3, 1, length=1)
    G.add_edge(2, 4, length=1)

    dist, path = astar(G, 1, 4, length_cost, zero_heuristic, trace=False)

    assert dist == 2
    assert path == [1, 2, 4]

def test_astar_with_admissible_heuristic():
    """
    Heuristic underestimates distance -> A* still optimal
    """
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, length=2)
    G.add_edge(2, 3, length=2)
    G.add_edge(1, 3, length=10)

    def h(n):
        return 0 if n == 3 else 1

    dist, path = astar(G, 1, 3, length_cost, h, trace=False)

    assert dist == 4
    assert path == [1, 2, 3]


def test_astar_with_inadmissible_heuristic():
    """
    Heuristic overestimates -> A* may still find a path, but not guaranteed optimal
    Testing it finds a "valid path"
    """
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, length=2)
    G.add_edge(2, 3, length=2)
    G.add_edge(1, 3, length=10)

    # Overestimates cost
    def h(n):
        return 100

    dist, path = astar(G, 1, 3, length_cost, h, trace=False)

    # A* might choose the direct edge due to heuristic bias
    assert path in ([1, 2, 3], [1, 3])
    assert dist in (4, 10)'''