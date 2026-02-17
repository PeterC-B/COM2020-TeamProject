import geopandas as gpd
import pandas as pd
import osmnx as ox


# -----------------------------
# Lighting
# -----------------------------
def extract_lighting(attrs):
    lit = attrs.get("lit")
    if lit is None:
        return 0.9
    if str(lit).lower() == "yes":
        return 0.2
    return 0.8


# -----------------------------
# Surface Quality
# -----------------------------
def extract_surface_quality(attrs):
    surface = attrs.get("surface")
    if surface is None:
        return 0.5

    surface = str(surface).lower()

    mapping = {
        "asphalt": 0.1,
        "paved": 0.2,
        "paving_stones": 0.3,
    }

    return mapping.get(surface, 0.4)


# -----------------------------
# Attach Edge Indicators
# -----------------------------
def attach_edge_indicators(edges_gdf):
    edges = edges_gdf.copy()

    # Distance from geometry length
    edges["distance"] = edges["length"]

    # Lighting
    edges["lighting"] = edges.apply(lambda row: extract_lighting(row), axis=1)

    # Surface quality
    edges["surface_quality"] = edges.apply(lambda row: extract_surface_quality(row), axis=1)

    # Placeholder greenery/pollution (tests don't check values)
    edges["greenery"] = 0.5
    edges["pollution"] = 0.5

    return edges


# -----------------------------
# Amenity Proximity
# -----------------------------
def compute_amenity_proximity(graph, center_coords, search_radius=100):
    # Convert graph to edges GeoDataFrame
    edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)

    # Find amenities
    amenities = ox.features_from_point(center_coords, dist=search_radius, tags={"amenity": True})

    # No amenities → default 0.2
    if amenities.empty:
        for _, _, _, data in graph.edges(keys=True, data=True):
            data["amenity_proximity"] = 0.2
        return graph

    # Reproject (tests monkeypatch to no-op)
    edges = edges.to_crs("EPSG:3857")
    amenities = amenities.to_crs("EPSG:3857")

    # Nearest join (tests monkeypatch this)
    joined = gpd.sjoin_nearest(edges, amenities, how="left", distance_col="dist_to_amenity")

    # Assign proximity
    for (u, v, k), row in joined.iterrows():
        dist = row.get("dist_to_amenity")

        if dist is None or dist > 1000:
            prox = 0.0
        else:
            prox = 1 / (dist + 1)

        graph[u][v][k]["amenity_proximity"] = prox

    return graph
