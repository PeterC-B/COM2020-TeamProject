"""
Weight utilities:
    - Validate weight dictionaries
    - Apply defaults
    - Clamp values to valid ranges
"""

import geopandas as gpd

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
    return (1-safety_priority) * lighting

def calculate_speed_score(edge_data : gpd.GeoDataFrame, speed_priority : float):
    speed = edge_data.get("surface_quality") * 4.8
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

    edges_gdf_copy["safety_score"] = edges_gdf_copy.apply(calculate_safety_score, axis=1, args=(safety_priority,))
    edges_gdf_copy["speed_score"] = edges_gdf_copy.apply(calculate_speed_score, axis=1, args=(speed_priority,))
    edges_gdf_copy["greenery_score"] = edges_gdf_copy.apply(calculate_greenery_score, axis=1, args=(greenery_priority,))

    edges_gdf_copy["weight"] = edges_gdf_copy.apply(calculate_weight, axis=1)

    return edges_gdf_copy