import pytest
import networkx as nx
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

@pytest.fixture
def small_edges_gdf():
    # Minimal edges GeoDataFrame with MultiIndex (u, v, key)
    data = {
        "length": [10.0, 20.0],
        "lit": [None, "yes"],
        "highway": ["residential", "path"],
        "surface": [None, "asphalt"],
        "geometry": [LineString([(0,0),(1,1)]), LineString([(1,1),(2,2)])],
    }
    index = pd.MultiIndex.from_tuples([(1, 2, 0), (2, 3, 0)], names=["u", "v", "key"])
    gdf = gpd.GeoDataFrame(data, index=index, crs="EPSG:4326")
    return gdf

@pytest.fixture
def small_graph():
    G = nx.MultiDiGraph()
    G.add_node(1, x=0, y=0)
    G.add_node(2, x=1, y=1)
    G.add_node(3, x=2, y=2)
    G.add_edge(1, 2, key=0, length=10.0, lit=None, highway="residential", surface=None)
    G.add_edge(2, 3, key=0, length=20.0, lit="yes", highway="path", surface="asphalt")
    return G