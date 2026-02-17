import pytest
import networkx as nx
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString

import server.scripts.visualisation.visualisation_utils as vis

def test_ensure_graph_dir(monkeypatch):
    called = {"ok": False}

    def fake_makedirs(path, exist_ok):
        called["ok"] = True
        assert path == vis.GRAPH_DIR

    monkeypatch.setattr("server.scripts.visualisation.visualisation_utils.os.makedirs", fake_makedirs)

    vis.ensure_graph_dir()
    assert called["ok"] is True

def test_add_crime_rating_basic():
    df = gpd.GeoDataFrame({
        "access_score": [0.0005, 0.02, 0.1],
        "geometry": [Point(0,0), Point(1,1), Point(2,2)]
    })

    out = vis.add_crime_rating(df)

    assert list(out["score_band"]) == [1, 0.6, 0.1]

def test_add_crime_rating_with_colours(monkeypatch):
    df = gpd.GeoDataFrame({
        "access_score": [0.0005],
        "geometry": [Point(0,0)]
    })

    # Mock colour map to return a fixed hex
    class FakeCmap:
        def __call__(self, x):
            return (1, 0, 0, 1)  # red

    monkeypatch.setattr("server.scripts.visualisation.visualisation_utils.cm.get_cmap", lambda name: FakeCmap())
    monkeypatch.setattr("server.scripts.visualisation.visualisation_utils.mcolors.to_hex", lambda rgba: "#FF0000")

    out = vis.add_crime_rating(df, add_colours=True)
    assert out.loc[0, "edge_colour"] == "#FF0000"

def test_add_feature_to_graph(monkeypatch):
    G = nx.MultiDiGraph()
    ax = object()

    # Mock amenities
    amenities = gpd.GeoDataFrame({
        "geometry": [Point(0,0), Point(1,1)]
    })

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.features_from_point",
        lambda *a, **k: amenities
    )

    # Mock centroid + plot
    monkeypatch.setattr(
        amenities.__class__,
        "plot",
        lambda self, ax, color, label, alpha, markersize: None
    )

    vis.add_feature_to_graph(G, ax, (51.5, -2.6), ("Test", {"amenity": "bar"}, "#00FF00", 0.5, 20))

def test_add_lighting_tag(monkeypatch):
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, key=0, geometry=LineString([(0,0),(1,1)]))

    nodes = gpd.GeoDataFrame({"geometry": [Point(0,0)]}, index=[1])
    edges = gpd.GeoDataFrame(
        {"geometry": [LineString([(0,0),(1,1)])]},
        index=pd.MultiIndex.from_tuples([(1,2,0)], names=["u","v","key"])
    )

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.graph_to_gdfs",
        lambda graph: (nodes, edges)
    )

    # Mock lighting points
    lit = gpd.GeoDataFrame({"lit": ["yes"], "geometry": [Point(0,0)]})

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.features_from_point",
        lambda *a, **k: lit
    )

    # Mock CRS transforms
    monkeypatch.setattr(edges.__class__, "to_crs", lambda self, epsg: self)
    monkeypatch.setattr(lit.__class__, "to_crs", lambda self, epsg: self)

    # Mock spatial join
    joined = edges.copy()
    joined["lit"] = ["yes"]
    joined["lamp_dist"] = [1.0]

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.gpd.sjoin_nearest",
        lambda *a, **k: joined
    )

    # Mock graph_from_gdfs
    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.graph_from_gdfs",
        lambda n, e: "GRAPH"
    )

    out = vis.add_lighting_tag(G, (51.5, -2.6), 100)
    assert out == "GRAPH"

def test_add_surface_tag(monkeypatch):
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, key=0, geometry=LineString([(0,0),(1,1)]))

    nodes = gpd.GeoDataFrame({"geometry": [Point(0,0)]}, index=[1])
    edges = gpd.GeoDataFrame(
        {"geometry": [LineString([(0,0),(1,1)])]},
        index=pd.MultiIndex.from_tuples([(1,2,0)], names=["u","v","key"])
    )

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.graph_to_gdfs",
        lambda graph: (nodes, edges)
    )

    surface = gpd.GeoDataFrame({"surface": ["paved"], "geometry": [Point(0,0)]})

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.features_from_point",
        lambda *a, **k: surface
    )

    monkeypatch.setattr(edges.__class__, "to_crs", lambda self, epsg: self)
    monkeypatch.setattr(surface.__class__, "to_crs", lambda self, epsg: self)

    joined = edges.copy()
    joined["surface"] = ["paved"]
    joined["surface_dist"] = [1.0]

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.gpd.sjoin_nearest",
        lambda *a, **k: joined
    )

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.graph_from_gdfs",
        lambda n, e: "GRAPH"
    )

    out = vis.add_surface_tag(G, (51.5, -2.6), 100)
    assert out == "GRAPH"

def test_print_shortest_path_graph(monkeypatch):
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, key=0)
    G.add_node(1)
    G.add_node(2)

    nodes = gpd.GeoDataFrame({"node_colour": ["#FFF"], "node_size": [10], "node_alpha": [1]}, index=[1])
    edges = gpd.GeoDataFrame({"u":[1], "v":[2], "edge_colour":["#CCC"], "edge_alpha":[0.4]})

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.graph_to_gdfs",
        lambda graph: (nodes.copy(), edges.copy())
    )

    # Mock graph rebuild
    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.graph_from_gdfs",
        lambda n, e: "GRAPH"
    )

    # Mock plot_graph
    class FakeFig:
        def savefig(self, *a, **k): pass

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.plot_graph",
        lambda *a, **k: (FakeFig(), None)
    )

    vis.print_shortest_path_graph(G, [1,2])

def test_plot_crime_graph(monkeypatch):
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, key=0)

    nodes = gpd.GeoDataFrame({"geometry":[Point(0,0)]}, index=[1])
    edges = gpd.GeoDataFrame({"access_score":[0.01], "geometry":[LineString([(0,0),(1,1)])]})
    edges["edge_colour"] = ["#FF0000"]

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.graph_to_gdfs",
        lambda graph: (nodes, edges)
    )

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.plot_graph",
        lambda *a, **k: (type("F", (), {"savefig": lambda self,*a,**k: None})(), None)
    )

    vis.plot_crime_graph(G)

def test_plot_blank_graph(monkeypatch):
    G = nx.MultiDiGraph()

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.graph_from_point",
        lambda *a, **k: G
    )

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.plot_graph",
        lambda *a, **k: (type("F", (), {"savefig": lambda self,*a,**k: None})(), None)
    )

    out = vis.plot_blank_graph((51.5,-2.6), 100, "walk")
    assert out is G

def test_plot_filled_graph(monkeypatch):
    G = nx.MultiDiGraph()

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.plot_blank_graph",
        lambda *a, **k: G
    )

    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.ox.plot_graph",
        lambda *a, **k: (type("F", (), {"savefig": lambda self,*a,**k: None})(), None)
    )

    # Mock add_feature_to_graph
    monkeypatch.setattr(
        "server.scripts.visualisation.visualisation_utils.add_feature_to_graph",
        lambda *a, **k: None
    )

    out = vis.plot_filled_graph(
        features=[("Test", {"amenity":"bar"}, "#00FF00", 0.5, 20)],
        coords=(51.5,-2.6),
        radius=100,
        travel_type="walk"
    )

    assert out is G
