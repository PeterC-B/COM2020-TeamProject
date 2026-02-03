"""
Indicator extraction and processing utilities

This package contains modules responsible for:
    - Extracting Healthy Streets attributes from raw OSMnx edges
    - Computing derived indicators such as amenity proximity
    - Normalising indicator values for routing and scoring

All modules here operate directly on NetworkX MultiDiGraphs and
GeoDataFrames, and contain no side effects on import
"""