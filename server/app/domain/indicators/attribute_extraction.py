"""
Healthy Streets Attribute Extraction

This module attaches deterministic, OSM-tag-based indicators to each
edge in a NetworkX MultiDiGraph. It is used during preprocessing only.

Indicators extracted:
    - distance (meters)
    - lighting (0–1)
    - greenery (0–1)
    - pollution (0–1)
    - surface_quality (0–1)
    - amenity_proximity (0–1, computed separately)
"""
import geopandas as gpd
import networkx as nx
import osmnx as ox


# Lighting
# -----------------------------
def extract_lighting(edge_data):
    lit = edge_data.get("lit")

    if lit is None:
        return 0.0

    lit = str(lit).lower()

    if lit == "yes":
        return 1.0
    if lit in {"limited", "interval", "automatic"}:
        return 0.5

    return 0.0


# Greenery
# -----------------------------
def extract_greenery(edge_data):
    highway = edge_data.get("highway")

    if isinstance(highway, list):
        highway = highway[0]

    if highway is None:
        return 0.3

    highway = str(highway).lower()

    if highway in {"path", "footway", "cycleway", "bridleway"}:
        return 0.9

    if edge_data.get("landuse") in {"forest", "grass", "meadow", "park"}:
        return 0.9

    if highway in {"residential", "living_street"}:
        return 0.6

    if highway in {"primary", "secondary", "tertiary"}:
        return 0.3

    if highway in {"motorway", "trunk"}:
        return 0.1

    return 0.4


# Pollution
# -----------------------------
def extract_pollution(edge_data):
    highway = edge_data.get("highway")

    if isinstance(highway, list):
        highway = highway[0]

    if highway is None:
        return 0.3

    highway = str(highway).lower()

    if highway in {"motorway", "trunk"}:
        return 1.0

    if highway in {"primary", "secondary"}:
        return 0.7

    if highway in {"tertiary", "residential"}:
        return 0.4

    if highway in {"footway", "cycleway", "path"}:
        return 0.1

    return 0.3


# Surface Quality
# -----------------------------
def extract_surface_quality(edge_data):
    surface = edge_data.get("surface")

    if surface is None:
        return 0.5

    surface = str(surface).lower()

    good = {"paved", "asphalt", "concrete", "paving_stones"}
    medium = {"compacted", "fine_gravel", "gravel"}
    poor = {"dirt", "earth", "mud", "sand", "grass"}

    if surface in good:
        return 1.0
    if surface in medium:
        return 0.6
    if surface in poor:
        return 0.2

    return 0.5


# Main extraction function
# -----------------------------
def attach_edge_indicators(graph: nx.MultiDiGraph):
    """
    Attach all Healthy Streets indicators to each edge.
    """

    for _, _, _, data in graph.edges(keys=True, data=True):
        data["distance"] = data.get("length", 1)
        data["lighting"] = extract_lighting(data)
        data["greenery"] = extract_greenery(data)
        data["pollution"] = extract_pollution(data)
        data["surface_quality"] = extract_surface_quality(data)

    return graph


def compute_amenity_proximity(graph, center_coords, search_radius=450):
    """
    Compute amenity proximity for each edge using spatial distance to nightlife amenities.
    """

    edges_gdf = ox.graph_to_gdfs(graph, nodes=False, edges=True)

    amenities = ox.features_from_point(
        center_coords,
        tags={"amenity": ["bar", "pub", "nightclub", "casino", "biergarten", "gambling"]},
        dist=search_radius,
    )

    if amenities.empty:
        for _, _, _, data in graph.edges(keys=True, data=True):
            data["amenity_proximity"] = 0.2
        return graph

    edges_m = edges_gdf.to_crs(epsg=27700)
    amenities_m = amenities.to_crs(epsg=27700)

    joined = gpd.sjoin_nearest(
        edges_m,
        amenities_m,
        how="left",
        distance_col="dist_to_amenity",
    )

    def decay(d):
        if d is None:
            return 0.2
        if d > 1000:
            return 0.0
        return 1 / (d + 1)

    joined["amenity_proximity"] = joined["dist_to_amenity"].apply(decay)

    for (_, row) in joined.iterrows():
        u = row["u"]
        v = row["v"]
        key = row["key"]
        graph[u][v][key]["amenity_proximity"] = row["amenity_proximity"]

    return graph