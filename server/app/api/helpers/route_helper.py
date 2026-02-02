from server.app.domain.routing.algorithms.astar_algorithm import astar
from server.app.domain.routing.algorithms.yen_algorithm import yens
from server.app.domain.routing.algorithms.dijkstra_algorithm import dijkstra
import geopandas as gpd
import networkx as nx

def run_route_algorithm(graph : nx.MultiDiGraph, route_algorithm : function = yens):
    