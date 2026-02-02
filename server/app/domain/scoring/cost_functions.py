"""
Cost functions for routing.

Defines:
    - Healthy Streets attribute schema
    - Main cost function for routing algorithms
    - Debugging breakdown helper
"""

from server.app.domain.indicators.normalisation import normalise_edge_attributes


# Healthy Streets attribute schema
HS_ATTRIBUTES = {
    "distance": {
        "description": "Length of the edge in meters",
        "default": 0.0,
        "normalise": False
    },
    "lighting": {
        "description": "Lighting quality (0–1)",
        "default": 0.5,
        "normalise": True
    },
    "greenery": {
        "description": "Greenery score (0–1)",
        "default": 0.5,
        "normalise": True
    },
    "pollution": {
        "description": "Pollution level (0–1)",
        "default": 0.5,
        "normalise": True
    },
    "surface_quality": {
        "description": "Surface quality (0–1)",
        "default": 0.5,
        "normalise": True
    },
    "amenity_proximity": {
        "description": "Amenity proximity score (0–1)",
        "default": 0.2,
        "normalise": True
    }
}


# Default user weights (fallback)
DEFAULT_WEIGHTS = {
    "distance": 1.0,
    "lighting": 1.0,
    "greenery": 1.0,
    "pollution": 1.0,
    "surface_quality": 1.0,
    "amenity_proximity": 1.0,
}


def healthy_cost(edge_data, weights=None):
    """
    Compute the routing cost for a single edge.

    edge_data: dict of edge attributes
    weights: dict of user-provided weights (optional)

    Returns:
        numeric cost
    """

    # Use defaults if no weights provided
    if weights is None:
        weights = DEFAULT_WEIGHTS

    # Normalise indicators (distance stays raw)
    edge = normalise_edge_attributes(edge_data, HS_ATTRIBUTES)

    # Scale distance so it doesn't dominate
    distance = edge.get("distance", 1)
    distance_scaled = distance / 100.0  # convert meters → ~0–10 range

    total_cost = 0

    for attr, weight in weights.items():
        if attr == "distance":
            total_cost += weight * distance_scaled
        elif attr in edge:
            total_cost += weight * edge[attr]

    return total_cost


def explain_cost(edge_data, weights=None):
    """
    Return a breakdown of how each attribute contributed to the final cost.
    """

    if weights is None:
        weights = DEFAULT_WEIGHTS

    edge = normalise_edge_attributes(edge_data, HS_ATTRIBUTES)

    distance = edge.get("distance", 1)
    distance_scaled = distance / 100.0

    breakdown = {}

    for attr, weight in weights.items():
        if attr == "distance":
            value = distance_scaled
        else:
            value = edge.get(attr)

        if value is not None:
            breakdown[attr] = {
                "value": value,
                "weight": weight,
                "contribution": value * weight
            }

    breakdown["total_cost"] = sum(
        item["contribution"] for item in breakdown.values()
    )

    return breakdown