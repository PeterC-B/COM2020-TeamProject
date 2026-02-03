import pytest
from math import inf

from server.app.domain.routing.algorithms.yen_algorithm import yens, compute_path_length



# Yen Algorithm testing for the non MultiDiGraph version
# Helpers
def simple_graph():
    return {
        1: {2: 1},
        2: {3: 1},
        3: {4: 1},
        4: {}
    }

def branching_graph():
    return {
        1: {2: 10, 3: 1},
        2: {4: 10},
        3: {4: 1},
        4: {}
    }

def cycle_graph():
    return {
        1: {2: 1},
        2: {3: 1, 4: 1},
        3: {1: 1},
        4: {}
    }

# Tests
def test_compute_path_length_basic():
    graph = {
        1: {2: 5},
        2: {3: 7},
        3: {}
    }
    path = [1, 2, 3]
    assert compute_path_length(graph, path) == 12

def test_compute_path_length_missing_edge():
    graph = {1: {2: 5}, 2: {}}
    path = [1, 2, 3]
    assert compute_path_length(graph, path) == 5  # 2 -> 3 missing -> KeyError avoided by test design

def test_yens_single_path():
    graph = simple_graph()
    paths = yens(graph, 1, 4, k_paths=1, trace=False)
    assert paths == [[1, 2, 3, 4]]

def test_yens_two_paths_equal_cost():
    """
    Graph:
        1 -> 2 -> 4 cost 2
        1 -> 3 -> 4 cost 2
    """
    graph = {
        1: {2: 1, 3: 1},
        2: {4: 1},
        3: {4: 1},
        4: {}
    }

    paths = yens(graph, 1, 4, k_paths=2, trace=False)

    assert len(paths) == 2
    assert [1, 2, 4] in paths
    assert [1, 3, 4] in paths

def test_yens_k_greater_than_available():
    graph = simple_graph()
    paths = yens(graph, 1, 4, k_paths=5, trace=False)
    assert paths == [[1, 2, 3, 4]]

def test_yens_no_path():
    graph = {1: {2: 1}, 2: {}, 3: {}}
    paths = yens(graph, 1, 3, k_paths=3, trace=False)
    assert paths == []

def test_yens_cycle_handling():
    """
    Graph:
        1 -> 2 -> 3 -> 1 (cycle)
        2→4
    Shortest path to 4 is 1 -> 2 -> 4
    """
    graph = cycle_graph()
    paths = yens(graph, 1, 4, k_paths=3, trace=False)

    assert paths[0] == [1, 2, 4]

def test_yens_path_ordering():
    """
    Two paths:
        1 -> 3 -> 4 cost 2
        1 -> 2 -> 4 cost 10
    """
    graph = branching_graph()
    paths = yens(graph, 1, 4, k_paths=2, trace=False)

    assert paths[0] == [1, 3, 4]
    assert paths[1] == [1, 2, 4]

def test_yens_graph_restoration():
    """
    Ensures Yen’s restores the graph after each spur iteration
    If not restored, later paths will be missing edges
    """
    graph = branching_graph()
    yens(graph, 1, 4, k_paths=2, trace=False)

    # Graph must remain unchanged
    assert graph[1][2] == 10
    assert graph[1][3] == 1
    assert graph[2][4] == 10
    assert graph[3][4] == 1

def test_yens_three_paths():
    """
    Graph with 3 loopless paths:
        1 -> 2 -> 5
        1 -> 3 -> 5
        1 -> 4 -> 5
    """
    graph = {
        1: {2: 1, 3: 2, 4: 3},
        2: {5: 1},
        3: {5: 1},
        4: {5: 1},
        5: {}
    }

    paths = yens(graph, 1, 5, k_paths=3, trace=False)

    assert paths[0] == [1, 2, 5]
    assert paths[1] == [1, 3, 5]
    assert paths[2] == [1, 4, 5]