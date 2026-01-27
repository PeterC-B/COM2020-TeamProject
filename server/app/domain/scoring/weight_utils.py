"""
Weight utilities:
    - Validate weight dictionaries
    - Apply defaults
    - Clamp values to valid ranges
"""

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