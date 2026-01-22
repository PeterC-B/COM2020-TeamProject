"""
Attribute Extraction:
    - Extracts lighting, greenery, pollution, surface, quality, etc.
    - Normalises values to 0-1
    - Attatch attributes to each edge in the OSMnx graph
"""

# Extracts lighting score from OSM tags
def extract_lighting(edge_data):
    pass

# Compute greenery score for an edge
def extract_greenery(edge_data, graph, u, v):
    pass

# Compute pollution proxy score based on road type
def extract_pollution(edge_data):
    pass

# Compute surface quality score
def extract_surface_quality(edge_data):
    pass

def extract_edge_attributes(graph):
    """
    Loop through all edge and attach:
        - distance
        - lighting
        - greenery
        - pollution
        - surface_quality
    Returns the modified graph
    """
    pass