'''import pytest
import networkx as nx
from math import inf
from tests.load_module import load_module

astar_algorithm = load_module("server/app/domain/routing/algorithms/astar_algorithm.py")
astar = astar_algorithm.astar

from tests.utils.algorithm_diag import log_algorithm_diagnostic

# Helpers
def unit_cost(edge_data):
    return 1

def length_cost(edge_data):
    return edge_data.get("length", 1)

def zero_heuristic(node):
    return 0

def simple_heuristic(node):
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

    expected = {"distance": 3, "path": [1, 2, 3, 4]}
    actual = {"distance": dist, "path": path}
    log_algorithm_diagnostic("A*: simple chain", expected, actual)

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

    expected = {"distance": 2, "path": [1, 3, 4]}
    actual = {"distance": dist, "path": path}
    log_algorithm_diagnostic("A*: branching paths", expected, actual)

    assert dist == 2
    assert path == [1, 3, 4]


def test_astar_no_path():
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, length=1)

    dist, path = astar(G, 1, 3, length_cost, zero_heuristic, trace=False)

    expected = {"distance": inf, "path": []}
    actual = {"distance": dist, "path": path}
    log_algorithm_diagnostic("A*: no path", expected, actual)

    assert dist == inf
    assert path == []


def test_astar_source_equals_target():
    G = nx.MultiDiGraph()
    G.add_node(5)

    dist, path = astar(G, 5, 5, length_cost, zero_heuristic, trace=False)

    expected = {"distance": 0, "path": [5]}
    actual = {"distance": dist, "path": path}
    log_algorithm_diagnostic("A*: source == target", expected, actual)

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

    expected = {"distance": 2, "path": [1, 2, 3]}
    actual = {"distance": dist, "path": path}
    log_algorithm_diagnostic("A*: multiedges", expected, actual)

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

    expected = {"distance": 2, "path": [1, 2, 4]}
    actual = {"distance": dist, "path": path}
    log_algorithm_diagnostic("A*: cycle handling", expected, actual)

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

    expected = {"distance": 4, "path": [1, 2, 3]}
    actual = {"distance": dist, "path": path}
    log_algorithm_diagnostic("A*: admissible heuristic", expected, actual)

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

    def h(n):
        return 100  # overestimates

    dist, path = astar(G, 1, 3, length_cost, h, trace=False)

    expected = {"valid_paths": [[1, 2, 3], [1, 3]]}
    actual = {"valid_paths": [path]}
    log_algorithm_diagnostic("A*: inadmissible heuristic", expected, actual)

    assert path in ([1, 2, 3], [1, 3])
    assert dist in (4, 10)'''