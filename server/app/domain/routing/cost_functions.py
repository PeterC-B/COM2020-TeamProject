"""
Cost functions (defines):
    - The attribute schema
    - The main cost function used by routing algorithms
    - A breakdown/ explanation helper for debugging or UI
"""
from .normalisation import normalise_edge_attributes

# Attribute schema
HS_ATTRIBUTES = {
    "distance": {
        "description": "Length of the edge in meters",
        "default": None,
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
    # Add more attributes as needed
}

# Main cost function
def healthy_cost(edge_data, weights):
    """
    Compute the cost for a single edge

    edge_data: dict of raw edge attributes
    weights: dict of user-provided weights

    Returns a single numeric cost
    """
    edge = normalise_edge_attributes(edge_data, HS_ATTRIBUTES)

    total_cost = 0

    for attr, weight in weights.items():
        if attr in edge:
            total_cost += weight * edge[attr]
    return total_cost

# Debugging helper
def explain_cost(edge_data, weights):
    """
    Return a breakdown of how each attribute contributed to the final cost
    """
    edge = normalise_edge_attributes(edge_data, HS_ATTRIBUTES)

    breakdown = {}

    for attr, weight in weights.items():
        if attr in edge:
            breakdown[attr] = {
                "value": edge[attr],
                "weight": weight,
                "contribution": edge[attr] * weight
            }
    breakdown["total_cost"] = sum(item["contribution"] for item in breakdown.values())
    
    return breakdown