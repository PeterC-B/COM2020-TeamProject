"""
Coordinate validation utilities.
"""

def validate_coordinates(coords):
    """
    Validate that coords represent a (lat, lon) pair.

    Accepts:
        - (lat, lon)
        - [lat, lon]
        - {"lat": x, "lon": y}
        - "lat,lon"

    Returns:
        True if valid, False otherwise.
    """

    # Handle dict input
    if isinstance(coords, dict):
        if "lat" in coords and "lon" in coords:
            coords = (coords["lat"], coords["lon"])
        else:
            return False

    # Handle string input: "lat,lon"
    if isinstance(coords, str):
        parts = coords.split(",")
        if len(parts) != 2:
            return False
        coords = (parts[0].strip(), parts[1].strip())

    # Must now be list/tuple
    if not isinstance(coords, (list, tuple)) or len(coords) != 2:
        return False

    lat, lon = coords

    # Convert to floats
    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return False

    # Bounds check
    if not (-90 <= lat <= 90):
        return False
    if not (-180 <= lon <= 180):
        return False

    return True