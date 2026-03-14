import pytest
from math import inf
from tests.load_module import load_module

dijkstra_algorithm = load_module("server/app/domain/routing/algorithms/dijkstra_algorithm.py")
dijkstra = dijkstra_algorithm.dijkstra
from tests.utils.algorithm_diag import log_algorithm_diagnostic


def test_dijkstra_simple_chain():
    graph = {1:{2:1}, 2:{3:1}, 3:{4:1}, 4:{}}

    dist, path = dijkstra(graph, 1, 4, trace=False)

    expected = {"distance": 3, "path": [1,2,3,4]}
    actual = {"distance": dist, "path": path}

    log_algorithm_diagnostic("Dijkstra: simple chain", expected, actual)

    assert dist == 3
    assert path == [1,2,3,4]


def test_dijkstra_branching_paths():
    graph = {
        1: {2: 10, 3: 1},
        2: {4: 10},
        3: {4: 1},
        4: {}
    }

    dist, path = dijkstra(graph, 1, 4, trace=False)

    expected = {"distance": 2, "path": [1,3,4]}
    actual = {"distance": dist, "path": path}

    log_algorithm_diagnostic("Dijkstra: branching paths", expected, actual)

    assert dist == 2
    assert path == [1, 3, 4]


def test_dijkstra_no_path():
    graph = {
        1: {2: 1},
        2: {},
        3: {}
    }

    dist, path = dijkstra(graph, 1, 3, trace=False)

    expected = {"distance": inf, "path": []}
    actual = {"distance": dist, "path": path}

    log_algorithm_diagnostic("Dijkstra: no path", expected, actual)

    assert dist == inf
    assert path == []


def test_dijkstra_source_equals_target():
    graph = {5: {}}

    dist, path = dijkstra(graph, 5, 5, trace=False)

    expected = {"distance": 0, "path": [5]}
    actual = {"distance": dist, "path": path}

    log_algorithm_diagnostic("Dijkstra: source == target", expected, actual)

    assert dist == 0
    assert path == [5]


def test_dijkstra_stale_queue_entries():
    graph = {
        1: {2: 10},
        2: {},
    }

    graph[1][2] = 1  # better path discovered later

    dist, path = dijkstra(graph, 1, 2, trace=False)

    expected = {"distance": 1, "path": [1,2]}
    actual = {"distance": dist, "path": path}

    log_algorithm_diagnostic("Dijkstra: stale queue entries", expected, actual)

    assert dist == 1
    assert path == [1, 2]


def test_dijkstra_cycle_handling():
    graph = {
        1: {2: 1},
        2: {3: 1, 4: 1},
        3: {1: 1},
        4: {}
    }

    dist, path = dijkstra(graph, 1, 4, trace=False)

    expected = {"distance": 2, "path": [1,2,4]}
    actual = {"distance": dist, "path": path}

    log_algorithm_diagnostic("Dijkstra: cycle handling", expected, actual)

    assert dist == 2
    assert path == [1, 2, 4]


def test_dijkstra_weighted_graph():
    graph = {
        1: {2: 5, 3: 2},
        2: {},
        3: {2: 1}
    }

    dist, path = dijkstra(graph, 1, 2, trace=False)

    expected = {"distance": 3, "path": [1,3,2]}
    actual = {"distance": dist, "path": path}

    log_algorithm_diagnostic("Dijkstra: weighted graph", expected, actual)

    assert dist == 3
    assert path == [1, 3, 2]


def test_dijkstra_disconnected_graph():
    graph = {
        1: {2: 1},
        2: {},
        10: {11: 1},
        11: {}
    }

    dist, path = dijkstra(graph, 1, 11, trace=False)

    expected = {"distance": inf, "path": []}
    actual = {"distance": dist, "path": path}

    log_algorithm_diagnostic("Dijkstra: disconnected graph", expected, actual)

    assert dist == inf
    assert path == []
