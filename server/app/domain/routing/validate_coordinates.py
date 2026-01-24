

def validate_coordinates(coords):
    """
    Validate that coord is a (lat, lon) pair of floats

    Returns:
        True if valid, False otherwise
    """

    if not isinstance(coords, (list, tuple)):
        return False
    
    if len(coords) != 2:
        return False
    
    lat, lon = coords

    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return False
    
    # Sanity Bounds
    if not (-90 <= lat <= 90):
        return False
    if not (-180 <= lon <= 180):
        return False
    
    return True