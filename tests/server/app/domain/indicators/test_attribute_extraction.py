import app.domain.indicators.attribute_extraction as ae
import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import LineString, Point


# Lighting extraction tests
def test_extract_lighting_missing():
    # file returns 0.9 when lit is missing
    assert ae.extract_lighting({}) == pytest.approx(0.9)


def test_extract_lighting_yes():
    # file returns 0.2 when lit == "yes"
    assert ae.extract_lighting({"lit": "yes"}) == pytest.approx(0.2)

def test_extract_lighting_other():
    # any other value returns 0.8
    assert ae.extract_lighting({"lit": "no"}) == pytest.approx(0.8)

def test_extract_lighting_confusion_matrix():
    inputs = [{}, {"lit": "yes"}, {"lit": "no"}]

    expected = ["0.9", "0.2", "0.8"]
    predicted = [str(ae.extract_lighting(x)) for x in inputs]

    assert_confusion(expected, predicted, labels=["0.2", "0.8", "0.9"], name="Lighting Extraction")

# Surface quality mapping tests
def test_extract_surface_quality_defaults_and_categories():
    assert ae.extract_surface_quality({}) == pytest.approx(0.5)
    assert ae.extract_surface_quality({"surface": "asphalt"}) == pytest.approx(0.1)
    assert ae.extract_surface_quality({"surface": "paved"}) == pytest.approx(0.2)
    assert ae.extract_surface_quality({"surface": "paving_stones"}) == pytest.approx(0.3)
    assert ae.extract_surface_quality({"surface": "unknown_surface"}) == pytest.approx(0.4)

def test_extract_surface_quality_confusion_matrix():
    inputs = [
        {},
        {"surface": "asphalt"},
        {"surface": "paved"},
        {"surface": "paving_stones"},
        {"surface": "unknown_surface"},
        {"surface": "asphalt"},
        {},
    ]

    expected = ["0.5", "0.1", "0.2", "0.3", "0.4", "0.1", "0.5"]
    predicted = [str(ae.extract_surface_quality(x)) for x in inputs]

    assert_confusion(expected, predicted, labels=["0.1", "0.2", "0.3", "0.4", "0.5"], name="Surface Quality")


# attach_edge_indicators: ensure new columns exist and values derived from input
def test_attach_edge_indicators_creates_columns(small_edges_gdf):
    out = ae.attach_edge_indicators(small_edges_gdf)
    for col in ["distance", "lighting", "greenery", "pollution", "surface_quality"]:
        assert col in out.columns
    assert out["distance"].iloc[0] == pytest.approx(10.0)
    assert out["distance"].iloc[1] == pytest.approx(20.0)

# compute_amenity_proximity: no amenities -> default assignment
def test_compute_amenity_proximity_no_amenities(monkeypatch, small_graph):
    # Mock ox.features_from_point to return empty GeoDataFrame
    monkeypatch.setattr(ae.ox, "features_from_point", lambda *args, **kwargs: gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326"))
    # Mock ox.graph_to_gdfs to return nodes, edges (edges used for projection)
    monkeypatch.setattr(ae.ox, "graph_to_gdfs", lambda G, nodes=True, edges=True: (None, gpd.GeoDataFrame()))
    out_graph = ae.compute_amenity_proximity(small_graph, (51.45, -2.58), search_radius=100)
    for _, _, _, data in out_graph.edges(keys=True, data=True):
        assert data.get("amenity_proximity") == pytest.approx(0.2)

# compute_amenity_proximity: amenities found -> assign computed proximity
def test_compute_amenity_proximity_with_amenities(monkeypatch, small_graph):
    # Prepare edges_gdf with MultiIndex
    data = {
        "length": [10.0, 20.0],
        "geometry": [LineString([(0,0),(1,1)]), LineString([(1,1),(2,2)])],
    }
    idx = pd.MultiIndex.from_tuples([(1,2,0),(2,3,0)], names=["u","v","key"])
    edges_gdf = gpd.GeoDataFrame(data, index=idx, crs="EPSG:4326")

    # Mock ox.graph_to_gdfs to return nodes, edges
    monkeypatch.setattr(ae.ox, "graph_to_gdfs", lambda G, nodes=False, edges=True: edges_gdf)

    # Mock features_from_point to return a GeoDataFrame with one amenity point
    amenities = gpd.GeoDataFrame({"geometry":[Point(0.5,0.5)]}, crs="EPSG:4326")
    monkeypatch.setattr(ae.ox, "features_from_point", lambda *args, **kwargs: amenities)

    # Mock to_crs to return same object (no reprojection needed for test)
    monkeypatch.setattr(edges_gdf, "to_crs", lambda epsg: edges_gdf)
    monkeypatch.setattr(amenities, "to_crs", lambda epsg: amenities)

    # Mock gpd.sjoin_nearest to return a joined GeoDataFrame with dist_to_amenity values
    joined = edges_gdf.copy()
    joined["dist_to_amenity"] = [10.0, 2000.0]  # one close, one far (>1000)
    def fake_sjoin_nearest(a, b, how, distance_col):
        return joined
    monkeypatch.setattr(ae.gpd, "sjoin_nearest", fake_sjoin_nearest)

    out_graph = ae.compute_amenity_proximity(small_graph, (51.45, -2.58), search_radius=100)
    expected_first = 1 / (10.0 + 1)
    expected_second = 0.0

    vals = []
    for _, _, _, data in out_graph.edges(keys=True, data=True):
        vals.append(data.get("amenity_proximity"))
    assert vals[0] == pytest.approx(expected_first)
    assert vals[1] == pytest.approx(expected_second)