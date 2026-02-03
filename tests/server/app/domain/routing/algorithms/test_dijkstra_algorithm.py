import pytest
from math import inf

from server.app.domain.routing.algorithms.dijkstra_algorithm import dijkstra


# Dijkstra testing for the non MultiDiGraph version
def test_dijkstra_simple_chain():
    """
    Graph:
        1 → 2 → 3 → 4
    All weights = 1
    """
    graph = {
        1: {2: 1},
        2: {3: 1},
        3: {4: 1},
        4: {}
    }

    dist, path = dijkstra(graph, 1, 4, trace=False)

    assert dist == 3
    assert path == [1, 2, 3, 4]

def test_dijkstra_branching_paths():
    """
    Graph:
        1 -> 2 -> 4 (cost 10)
        1 -> 3 -> 4 (cost 2)
    Should choose 1 -> 3 -> 4
    """
    graph = {
        1: {2: 10, 3: 1},
        2: {4: 10},
        3: {4: 1},
        4: {}
    }

    dist, path = dijkstra(graph, 1, 4, trace=False)

    assert dist == 2
    assert path == [1, 3, 4]

def test_dijkstra_no_path():
    """
    Graph:
        1 -> 2
    No route to 3
    """
    graph = {
        1: {2: 1},
        2: {},
        3: {}
    }

    dist, path = dijkstra(graph, 1, 3, trace=False)

    assert dist == inf
    assert path == []

def test_dijkstra_source_equals_target():
    """
    If source == target, distance = 0 and path = [node]
    """
    graph = {5: {}}

    dist, path = dijkstra(graph, 5, 5, trace=False)

    assert dist == 0
    assert path == [5]

# Priority queue behaviour
def test_dijkstra_stale_queue_entries():
    """
    Ensure stale PQ entries are skipped correctly
    Graph:
        1 -> 2 (cost 10)
        1 -> 2 (cost 1)  <-- better path discovered later
    """
    graph = {
        1: {2: 10},
        2: {},
    }

    # Simulate a better path discovered later
    # Add a second edge dynamically
    graph[1][2] = 1

    dist, path = dijkstra(graph, 1, 2, trace=False)

    assert dist == 1
    assert path == [1, 2]

def test_dijkstra_cycle_handling():
    """
    Graph with a cycle:
        1 -> 2 -> 3 -> 1
        2 → 4
    Shortest path to 4 is 1 -> 2 -> 4
    """
    graph = {
        1: {2: 1},
        2: {3: 1, 4: 1},
        3: {1: 1},
        4: {}
    }

    dist, path = dijkstra(graph, 1, 4, trace=False)

    assert dist == 2
    assert path == [1, 2, 4]

def test_dijkstra_weighted_graph():
    """
    Graph:
        1 -> 2 (cost 5)
        1 -> 3 (cost 2)
        3 -> 2 (cost 1)
    Shortest path to 2 is 1 -> 3 -> 2 (cost 3)
    """
    graph = {
        1: {2: 5, 3: 2},
        2: {},
        3: {2: 1}
    }

    dist, path = dijkstra(graph, 1, 2, trace=False)

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

    assert dist == inf
    assert path == []