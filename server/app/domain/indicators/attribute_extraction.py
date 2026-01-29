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
    - amenity_proximity (0–1)
"""
import geopandas as gpd
import networkx as nx
import osmnx as ox


# Lighting
# -----------------------------
def extract_lighting(edge_data):
    lit = edge_data.get("lit")

    if lit is None:
        return 0.8

    lit = str(lit).lower()

    if lit == "true":
        return 0.2

    return 0.8


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

    #good = {"paved", "asphalt", "concrete", "paving_stones"}
    #medium = {"compacted", "fine_gravel", "gravel"}
    #poor = {"dirt", "earth", "mud", "sand", "grass"}

    good = {"asphalt", "concrete"}
    medium = {"paved"}
    poor = {"paving_stones"}

    if surface in good:
        return 1.0
    if surface in medium:
        return 0.6
    if surface in poor:
        return 0.2

    return 0.5


# Main extraction function
# -----------------------------
def attach_edge_indicators(edges_gdf: gpd.GeoDataFrame):
    """
    Attach all Healthy Streets indicators to each edge.
    """

    edges_gdf_copy = edges_gdf.copy()

    edges_gdf_copy["distance"] = edges_gdf_copy["length"]
    edges_gdf_copy["lighting"] = edges_gdf_copy.apply(extract_lighting, axis=1)
    edges_gdf_copy["greenery"] = edges_gdf_copy.apply(extract_greenery, axis=1)
    edges_gdf_copy["pollution"] = edges_gdf_copy.apply(extract_pollution, axis=1)
    edges_gdf_copy["surface_quality"] = edges_gdf_copy.apply(extract_surface_quality, axis=1)

    return edges_gdf_copy


# Amenity Proximity (fixed for OSMnx 1.x)
# -----------------------------
def compute_amenity_proximity(graph, center_coords, search_radius=450):
    """
    Compute amenity proximity for each edge using spatial distance to nightlife amenities.
    Works with OSMnx 1.x (edges GeoDataFrame uses MultiIndex: (u, v, key)).
    """

    # Extract edges GeoDataFrame (MultiIndex: u, v, key)
    edges_gdf = ox.graph_to_gdfs(graph, nodes=False, edges=True)

    # Fetch nightlife amenities
    amenities = ox.features_from_point(
        center_coords,
        tags={"amenity": ["bar", "pub", "nightclub", "casino", "biergarten", "gambling"]},
        dist=search_radius,
    )

    # If no amenities found, assign default
    if amenities.empty:
        for _, _, _, data in graph.edges(keys=True, data=True):
            data["amenity_proximity"] = 0.2
        return graph

    # Project to metric CRS
    edges_m = edges_gdf.to_crs(epsg=27700)
    amenities_m = amenities.to_crs(epsg=27700)

    # Spatial join
    joined = gpd.sjoin_nearest(
        edges_m,
        amenities_m,
        how="left",
        distance_col="dist_to_amenity",
    )

    # Decay function
    def decay(d):
        if d is None:
            return 0.2
        if d > 1000:
            return 0.0
        return 1 / (d + 1)

    joined["amenity_proximity"] = joined["dist_to_amenity"].apply(decay)

    # Assign back to graph
    for idx, row in joined.iterrows():
        u, v, key = idx  # MultiIndex unpack
        graph[u][v][key]["amenity_proximity"] = row["amenity_proximity"]

    return graph

if __name__ == "__main__":
    from server.scripts.visualisation.visualisation_utils import plot_blank_graph, add_lighting_tag, add_surface_tag
    graph = plot_blank_graph((51.460498, -2.585757), 450, "walk")

    graph = add_lighting_tag(graph, (51.460498, -2.585757), 450)
    graph = add_surface_tag(graph, (51.460498, -2.585757), 450)
    fig, ax = ox.plot_graph(graph, show=False, close=False, node_size=2)
    fig.savefig("server/app/domain/indicators/graph.png", dpi=300)
    nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)
    edges_gdf.to_csv("server/app/domain/indicators/surface.csv")
    edges_gdf = attach_edge_indicators(edges_gdf)
    edges_export = edges_gdf.copy().reset_index()
    edges_export = edges_export[[
        "u", "v", "key",
        "distance",
        "lighting",
        "greenery",
        "pollution",
        "surface_quality",
    ]]
    edges_export.to_csv("server/app/domain/indicators/edges.csv")