"""
Normalisation utilities for attributes:
    - Scales values to 0-1
    - Applys defaults
    - Normalises all attributes for an edge
"""

def normalise_value(value, min_val=0, max_val=1):
    """
    Normalise a value to the 0-1 range
    If value is None, return 0.5 as a neutral fallback
    """
    if value is None:
        return 0.5
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)

def normalise_edge_attributes(edge_data, schema):
    """
    Apply normalisation rules to an edge's attributes

    schema: HS_ATTRIBUTES dict
    """
    normalised = {}

    for attr, meta in schema.items():
        raw_value = edge_data.get(attr, meta["default"])

        if meta["normalise"]:
            normalised[attr] = normalise_value(raw_value)
        else:
            normalised[attr] = raw_value
    return normalised