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
from app.models.location_model import LocationModel
from app.models.enums.LOCATION_TYPE import LocationType

AMENITY_TAGS = {
    "amenity":[
        "dentist", "doctors", "hospital", "clinic", "cinema", "library", "community_centre", "place_of_worship", "school", "cafe"
    ],
    "leisure":[
        "playground"
    ],
    "tourism":[
        "artwork"
    ]
}

# Lighting
# -----------------------------
def extract_lighting(edge_data):
    lit = edge_data.get("lit")

    if lit is None:
        return 0.9

    lit = str(lit).lower()

    if lit == "yes":
        return 0.1

    return 0.9


# Greenery
# -----------------------------
def extract_greenery(edge_data):
    highway = edge_data.get("highway")

    if isinstance(highway, list):
        highway = highway[0]

    if highway is None:
        return 0.3

    highway = str(highway).lower()

    if edge_data.get("landuse") in {"forest", "grass", "meadow", "park"}:
        return 0.6

    if highway in {"path", "footway", "cycleway", "bridleway"}:
        return 0.6

    if highway in {"residential", "living_street"}:
        return 0.5

    if highway in {"primary", "secondary", "tertiary"}:
        return 0.4

    if highway in {"motorway", "trunk"}:
        return 0.3

    return 0.5


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
        return 0.6

    if highway in {"primary", "secondary"}:
        return 0.5

    if highway in {"tertiary", "residential"}:
        return 0.4

    if highway in {"footway", "cycleway", "path"}:
        return 0.3

    return 0.5


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

    #good = {"asphalt", "concrete"}
    #medium = {"paved"}
    #poor = {"paving_stones"}

    if surface in good:
        return 0.9
    if surface in medium:
        return 1.0
    if surface in poor:
        return 1.1

    return 1.0


# Main extraction function
# -----------------------------
def attach_edge_indicators(edges_gdf: gpd.GeoDataFrame):
    """
    Attach all Healthy Streets indicators to each edge.
    """

    edges_gdf_copy = edges_gdf.copy()

    edges_gdf_copy["lighting"] = edges_gdf_copy.apply(extract_lighting, axis=1)
    edges_gdf_copy["greenery"] = edges_gdf_copy.apply(extract_greenery, axis=1)
    edges_gdf_copy["pollution"] = edges_gdf_copy.apply(extract_pollution, axis=1)
    edges_gdf_copy["surface_quality"] = edges_gdf_copy.apply(extract_surface_quality, axis=1)

    return edges_gdf_copy


# Amenity Proximity (fixed for OSMnx 1.x)
# -----------------------------
def compute_amenity_proximity(graph, center_coords, search_radius=500):
    """
    Compute amenity proximity for each edge using spatial distance to nightlife amenities.
    Works with OSMnx 1.x (edges GeoDataFrame uses MultiIndex: (u, v, key)).
    """

    pois = ox.features_from_point(
        center_point=center_coords,
        tags={"amenity": True},
        dist=search_radius
    ).head(50)

    locations = []

    lons = pois.geometry.x.tolist()
    lats = pois.geometry.y.tolist()

    nearest_nodes = ox.distance.nearest_nodes(graph, X=lons, Y=lats)

    for (_, row), node_id in zip(pois.iterrows(), nearest_nodes):

        lat = row.geometry.y
        lon = row.geometry.x

        node_id = ox.distance.nearest_nodes(graph, X=lon, Y=lat)

        location = LocationModel(
            name=row.get("name") or "Unknown",
            node_id=node_id,
            type=LocationType.GENERAL_AMENITY,
            information=row.get("amenity")
        )

        locations.append(location)
    return locations

if __name__ == "__main__":
    from scripts.visualisation.visualisation_utils import plot_blank_graph, add_lighting_tag, add_surface_tag
    graph = plot_blank_graph((51.460498, -2.585757), 450, "walk")

    graph = add_lighting_tag(graph, (51.460498, -2.585757), 450)
    graph = add_surface_tag(graph, (51.460498, -2.585757), 450)
    fig, ax = ox.plot_graph(graph, show=False, close=False, node_size=2)
    #fig.savefig("app/domain/indicators/graph.png", dpi=300)
    nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)
    edges_gdf.to_csv("app/domain/indicators/surface.csv")
    edges_gdf = attach_edge_indicators(edges_gdf)
    from app.domain.scoring.weight_utils import calculate_weights
    calculate_weights(edges_gdf, 0.3, 0.5, 0.9)
    edges_export = edges_gdf.copy().reset_index()
    edges_export = edges_export[[
        "u", "v", "key",
        "distance",
        "lighting",
        "greenery",
        "pollution",
        "surface_quality",
    ]]
    #edges_export.to_csv("app/domain/indicators/edges.csv")
