"""
Weight utilities:
    - Validate weight dictionaries
    - Apply defaults
    - Clamp values to valid ranges
"""
import server.app.api.helpers.algorithm_helper as help_algos
import geopandas as gpd
import osmnx as ox
import numpy as np

NODES_GDF = help_algos.nodes_csv_to_gdf()
EDGES_GDF = help_algos.edges_csv_to_gdf()

GRAPH = ox.graph_from_gdfs(NODES_GDF, EDGES_GDF)
COORDS = (51.460498, -2.585757)
DISTANCE = 450

# Full set of supported indicators
DEFAULT_WEIGHTS = {
    "distance": 1.0,
    "lighting": 1.0,
    "greenery": 1.0,
    "pollution": 1.0,
    "surface_quality": 1.0,
    "amenity_proximity": 1.0,
}


def validate_weights(weights):
    """
    Validate that:
        - weights is a dict
        - contains only valid keys
        - all values are numeric
        - all values are >= 0

    Returns:
        True if valid, False otherwise
    """

    if not isinstance(weights, dict):
        return False

    for key, value in weights.items():

        # Unknown attribute
        if key not in DEFAULT_WEIGHTS:
            return False

        # Must be numeric
        try:
            val = float(value)
        except (TypeError, ValueError):
            return False

        # Must be non-negative
        if val < 0:
            return False

    return True


def apply_default_weights(weights=None):
    """
    Fill missing weights with defaults.
    Clamp all values to >= 0.

    If weights is None, return DEFAULT_WEIGHTS.
    """

    if weights is None:
        return DEFAULT_WEIGHTS.copy()

    final = {}

    for key, default_val in DEFAULT_WEIGHTS.items():
        if key in weights:
            try:
                val = float(weights[key])
            except (TypeError, ValueError):
                val = default_val
        else:
            val = default_val

        # Clamp to >= 0
        if val < 0:
            val = 0.0

        final[key] = val

    return final



def calculate_safety_score(edge_data : gpd.GeoDataFrame, safety_priority : float):
    lighting = edge_data.get("lighting")
    drinking_place_distance = edge_data.get("normalised_pub_distance")
    return (1-safety_priority) * lighting * drinking_place_distance


def normalize_pub_distance(
    distance_to_pub: float,
    max_distance: float = 100.0,
    min_score: float = 0.4,
    max_score: float = 0.8
) -> float:
    """
    Normalize distance to nearest pub into a bounded risk score.
    Closer pubs = higher risk.
    Output is always within (min_score, max_score).
    """

    if distance_to_pub is None or np.isnan(distance_to_pub):
        return min_score

    # Clamp distance
    distance = min(distance_to_pub, max_distance)

    # Linear normalization (closer = higher risk)
    raw = 1.0 - (distance / max_distance)

    # Rescale to [min_score, max_score]
    return min_score + raw * (max_score - min_score)


def add_pub_distance(coords: tuple[int, int] = COORDS, distance : int = DISTANCE, nodes_gdf : gpd.GeoDataFrame = NODES_GDF, edges_gdf : gpd.GeoDataFrame = EDGES_GDF):
    pubs = ox.features_from_point(
        center_point=coords,
        tags={"amenity": ["pub", "bar", "biergarten", "casino", "nightclub", "gambling"]},
        dist=distance
    )

    edges_proj = edges_gdf.to_crs(epsg=27700)
    pubs_proj = pubs.to_crs(epsg=27700)

    edges_proj["edge_centroid"] = edges_proj.geometry.centroid
    pubs_proj["pub_centroid"] = pubs_proj.geometry.centroid

    joined = gpd.sjoin_nearest(
        edges_proj.set_geometry("edge_centroid"),
        pubs_proj.set_geometry("pub_centroid"),
        how="left",
        distance_col="distance_to_pub"
    )

    edges_gdf["distance_to_pub"] = joined["distance_to_pub"].fillna(distance)

    return edges_gdf


def calculate_speed_score(edge_data : gpd.GeoDataFrame, speed_priority : float):
    speed = edge_data.get("surface_quality")
    if(speed != 0):
        return speed * (1-speed_priority)
    return 999

def calculate_greenery_score(edge_data : gpd.GeoDataFrame, greenery_priority : float):
    greenery = edge_data.get("greenery")
    pollution = edge_data.get("pollution")
    return (1-greenery) * pollution * (1-greenery_priority)

def calculate_weight(edge_data : gpd.GeoDataFrame):
    greenery_score = edge_data.get("greenery_score")
    safety_score = edge_data.get("safety_score")
    speed_score = edge_data.get("speed_score")
    length = edge_data.get("length")

    return length * (greenery_score + safety_score + speed_score)

def calculate_weights(edges_gdf : gpd.GeoDataFrame, safety_priority : float, speed_priority : float, greenery_priority : float) -> gpd.GeoDataFrame:
    edges_gdf_copy = edges_gdf.copy()

    edges_gdf_copy = add_pub_distance(edges_gdf=edges_gdf_copy)
    edges_gdf_copy["normalised_pub_distance"] = (
        edges_gdf_copy["distance_to_pub"]
        .apply(normalize_pub_distance)
    )

    edges_gdf_copy.to_csv("server/server/app/domain/scoring/test_1.csv")

    edges_gdf_copy["safety_score"] = edges_gdf_copy.apply(calculate_safety_score, axis=1, args=(safety_priority,))
    edges_gdf_copy["speed_score"] = edges_gdf_copy.apply(calculate_speed_score, axis=1, args=(speed_priority,))
    edges_gdf_copy["greenery_score"] = edges_gdf_copy.apply(calculate_greenery_score, axis=1, args=(greenery_priority,))

    edges_gdf_copy["weight"] = edges_gdf_copy.apply(calculate_weight, axis=1)

    edges_gdf_copy.to_csv("server/server/app/domain/scoring/test.csv")