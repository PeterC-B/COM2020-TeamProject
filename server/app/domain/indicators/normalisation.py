"""
Normalisation utilities for Healthy Streets indicators.

This module:
    - Scales indicator values to 0–1
    - Applies defaults where needed
    - Normalises all indicator attributes on edges

Coordinates are NOT normalised here.
"""

def normalise_value(value, min_val=0, max_val=1):
    """
    Normalise a numeric value to the 0–1 range.
    If value is None or invalid, return 0.5 as a neutral fallback.
    """
    if value is None:
        return 0.5

    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0.5

    if max_val == min_val:
        return 0.5

    return (value - min_val) / (max_val - min_val)


def normalise_edge_attributes(edge_data, schema):
    """
    Apply normalisation rules to an edge's attributes.

    schema: dict defining:
        {
            "lighting": {"default": 0.0, "normalise": True},
            "greenery": {"default": 0.0, "normalise": True},
            ...
        }
    """
    normalised = {}

    for attr, meta in schema.items():
        raw_value = edge_data.get(attr, meta["default"])

        if meta.get("normalise", False):
            normalised[attr] = normalise_value(raw_value)
        else:
            normalised[attr] = raw_value

    return normalised


def normalise_graph_attributes(graph, schema=None):
    """
    Normalise all indicator attributes on a NetworkX MultiDiGraph.

    If no schema is provided, a default Healthy Streets schema is used.
    """

    if schema is None:
        schema = {
            "lighting": {"default": 0.0, "normalise": True},
            "greenery": {"default": 0.0, "normalise": True},
            "pollution": {"default": 0.0, "normalise": True},
            "surface_quality": {"default": 0.5, "normalise": True},
            "amenity_proximity": {"default": 0.2, "normalise": True},
        }

    for _, _, _, data in graph.edges(keys=True, data=True):
        normalised = normalise_edge_attributes(data, schema)
        data.update(normalised)

    return graph