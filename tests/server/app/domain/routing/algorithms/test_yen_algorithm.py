import pytest
from math import inf

from tests.utils.yen_core import yens, compute_path_length
from tests.utils.algorithm_diag import log_algorithm_diagnostic


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
    graph = {1: {2: 5}, 2: {3: 7}, 3: {}}
    path = [1, 2, 3]

    expected = 12
    actual = compute_path_length(graph, path)

    log_algorithm_diagnostic(
        "Yen: compute_path_length_basic",
        {"length": expected},
        {"length": actual}
    )

    assert actual == expected


def test_compute_path_length_missing_edge():
    graph = {1: {2: 5}, 2: {}}
    path = [1, 2, 3]

    expected = 5
    actual = compute_path_length(graph, path)

    log_algorithm_diagnostic(
        "Yen: compute_path_length_missing_edge",
        {"length": expected},
        {"length": actual}
    )

    assert actual == expected


def test_yens_single_path():
    graph = simple_graph()
    paths = yens(graph, 1, 4, k_paths=1, trace=False)

    expected = {"paths": [[1, 2, 3, 4]]}
    actual = {"paths": paths}

    log_algorithm_diagnostic("Yen: single path", expected, actual)

    assert paths == [[1, 2, 3, 4]]


def test_yens_two_paths_equal_cost():
    graph = {
        1: {2: 1, 3: 1},
        2: {4: 1},
        3: {4: 1},
        4: {}
    }

    paths = yens(graph, 1, 4, k_paths=2, trace=False)

    expected_paths = [[1, 2, 4], [1, 3, 4]]
    expected = {"paths": expected_paths}
    actual = {"paths": paths}

    log_algorithm_diagnostic("Yen: two equal-cost paths", expected, actual)

    assert len(paths) == 2
    assert [1, 2, 4] in paths
    assert [1, 3, 4] in paths


def test_yens_k_greater_than_available():
    graph = simple_graph()
    paths = yens(graph, 1, 4, k_paths=5, trace=False)

    expected = {"paths": [[1, 2, 3, 4]]}
    actual = {"paths": paths}

    log_algorithm_diagnostic("Yen: k > available", expected, actual)

    assert paths == [[1, 2, 3, 4]]


def test_yens_no_path():
    graph = {1: {2: 1}, 2: {}, 3: {}}
    paths = yens(graph, 1, 3, k_paths=3, trace=False)

    expected = {"paths": []}
    actual = {"paths": paths}

    log_algorithm_diagnostic("Yen: no path", expected, actual)

    assert paths == []


def test_yens_cycle_handling():
    graph = cycle_graph()
    paths = yens(graph, 1, 4, k_paths=3, trace=False)

    expected = {"paths": [[1, 2, 4]]}
    actual = {"paths": paths}

    log_algorithm_diagnostic("Yen: cycle handling", expected, actual)

    assert paths[0] == [1, 2, 4]


def test_yens_path_ordering():
    graph = branching_graph()
    paths = yens(graph, 1, 4, k_paths=2, trace=False)

    expected = {"paths": [[1, 3, 4], [1, 2, 4]]}
    actual = {"paths": paths}

    log_algorithm_diagnostic("Yen: path ordering", expected, actual)

    assert paths[0] == [1, 3, 4]
    assert paths[1] == [1, 2, 4]


def test_yens_graph_restoration():
    graph = branching_graph()
    yens(graph, 1, 4, k_paths=2, trace=False)

    expected = {
        "graph_restored": True
    }
    actual = {
        "graph_restored": (
            graph[1][2] == 10 and
            graph[1][3] == 1 and
            graph[2][4] == 10 and
            graph[3][4] == 1
        )
    }

    log_algorithm_diagnostic("Yen: graph restoration", expected, actual)

    assert actual["graph_restored"]


def test_yens_three_paths():
    graph = {
        1: {2: 1, 3: 2, 4: 3},
        2: {5: 1},
        3: {5: 1},
        4: {5: 1},
        5: {}
    }

    paths = yens(graph, 1, 5, k_paths=3, trace=False)

    expected = {"paths": [[1, 2, 5], [1, 3, 5], [1, 4, 5]]}
    actual = {"paths": paths}

    log_algorithm_diagnostic("Yen: three paths", expected, actual)

    assert paths[0] == [1, 2, 5]
    assert paths[1] == [1, 3, 5]
    assert paths[2] == [1, 4, 5]
