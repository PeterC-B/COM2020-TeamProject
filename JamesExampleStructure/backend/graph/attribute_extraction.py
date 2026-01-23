"""
Attribute Extraction:
    - Extracts lighting, greenery, pollution, surface, quality, etc.
    - Normalises values to 0-1
    - Attatch attributes to each edge in the OSMnx graph
"""
import osmnx as ox
import networkx as nx
import geopandas as gpd
import matplotlib.cm as cm
import matplotlib.colors as mcolors


#   Crime and Amenity Proximity scoring
# -------------------------------------------------------------------------------------------------
def add_distance_to_crime_spots(edges_gdf : gpd.GeoDataFrame, coords : tuple) -> gpd.GeoDataFrame:
    '''
    Compute proximity of edges to nightlife-related amenities (bars, pubs, casinos, etc.)
    Assigns an 'access_score' attribute
    
    :param edges_gdf: The GeoDataFrame that contains the edges in the chosen map
    :type edges_gdf: gpd.GeoDataFrame
    :param coords: The centre coordinates for the chosen area
    :type coords: tuple
    :return: The graph where edges are coloured based on their proximity to a place of drink
    :rtype: GeoDataFrame
    '''
    amenities = ox.features_from_point(
        coords,
        tags={"amenity":["bar", "biergarten", "pub", "casino", "nightclub", "gambling"]},
        dist=450,
    )

    edges_m = edges_gdf.to_crs(epsg=27700)
    amenities_m = amenities.to_crs(epsg=27700)

    nearest = gpd.sjoin_nearest(
        edges_m,
        amenities_m,
        how="left",
        distance_col="dist_to_amenity",
    )

    def distance_score(d):
        if d is None or d > 1000:
            return 0
        return 1 / (d+1)
    
    nearest["access_score"] = nearest["dist_to_amenity"].apply(distance_score)
    edges_gdf["access_score"] = nearest["access_score"].values

    return edges_gdf

def add_crime_rating(edges_gdf : gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    '''
    Convert access_score into a colour-coded crime heatmap
    
    :param edges_gdf: The GeoDataFrame containing all information on edges
    :type edges_gdf: gpd.GeoDataFrame
    :return: The updated edge GeoDataFrame with the hex values for the crime heatmap included
    :rtype: GeoDataFrame
    '''
    def score_band(d):
        if d < 0.001: return 1
        elif d < 0.0059: return 0.9
        elif d < 0.0108: return 0.8
        elif d < 0.0157: return 0.7
        elif d < 0.0206: return 0.6
        elif d < 0.0255: return 0.5
        elif d < 0.0304: return 0.4
        elif d < 0.0353: return 0.3
        elif d < 0.0402: return 0.2
        elif d < 0.0451: return 0.1
        else: return 0

    edges_gdf["score_band"] = edges_gdf["access_score"].apply(score_band)

    cmap = cm.get_cmap("RdYlGn")
    edges_gdf["edge_colour"] = edges_gdf["score_band"].apply(
        lambda x: mcolors.to_hex(cmap(x))
    )
    return edges_gdf

# Feature Plotting
# ----------------------------------------------------------------------------
def add_feature_to_graph(graph : nx.MultiDiGraph,
                          line, 
                          coords : tuple, 
                          feature : list, 
                          limit_amenities : bool = True) -> gpd.GeoDataFrame:
    '''
    Adds all features given to a graph of an area
    
    :param graph: The graph of the chosen area that has been generated
    :type graph: nx.MultiDiGraph
    :param line: The figure already generated
    :param coords: A tuple of the coordinates on Earth that the area is centered around
    :type coords: tuple
    :param feature: The list of features that you want to add to the graph
    :type feature: list
    :param limit_amenities: Are we limiting the amount of POIs to 80?
    :type limit_amenities: bool
    :return: The update GDF of the graph
    :rtype: gpd.GeoDataFrame
    '''
    features = ox.features_from_point(
        center_point=coords,
        tags=feature[1],
        dist=450,
    )

    if feature[0] == "Amenities" and limit_amenities:
        if len(features) >= 80:
            features = features.sample(n=80, random_state=42)
        else:
            features = features.copy()


    features["centroid"] = features.geometry.centroid

    features["nearest_node"] = ox.distance.nearest_nodes(
        graph,
        X=features.centroid.x,
        Y=features.centroid.y
    )

    features.plot(
        ax=line,
        color=feature[2],
        label=feature[0],
        alpha=feature[3],
        markersize=feature[4],
    )

def extract_lighting(edge_data):
    """
    Extracts lighting score from OSM tags
    """
    lit = edge_data.get("lit")

    if lit is None:
        return 0.0
    
    lit = str(lit).lower()

    if lit == "yes":
        return 1.0
    if lit in {"limited", "interval", "automatic"}:
        return 0.5
    return 0.0

# Compute greenery score for an edge
def extract_greenery(edge_data, graph, u, v):
    highway = edge_data.get("highway")

    if highway is None:
        return 0.3
    
    if isinstance(highway, list):
        highway = highway[0]
    
    highway = str(highway).lower()

    # Very green environments
    if highway in {"path", "footway", "cycleway", "bridleway"}:
        return 0.9
    
    if edge_data.get("landuse") in {"forest", "grass", "meadow", "park"}:
        return 0.9
    
    # Residential streets
    if highway in {"residential", "living_street"}:
        return 0.6
    
    # Main roads (less greenery generally)
    if highway in {"primary", "secondary", "tertiary"}:
        return 0.3
    
    # Motorways or industrial areas
    if highway in {"motorway", "trunk"}:
        return 0.1
    
    return 0.4  # fallback

# Compute pollution proxy score based on road type
def extract_pollution(edge_data):
    highway = edge_data.get("highway")

    if highway is None:
        return 0.3
    
    if isinstance(highway, list):
        highway = highway[0]
    
    highway = str(highway).lower()

    # Very polluted
    if highway in {"motorway", "trunk"}:
        return 1.0
    
    # Moderately polluted
    if highway in {"primary", "secondary"}:
        return 0.7
    
    # Lightly polluted
    if highway in {"tertiary", "residential"}:
        return 0.4
    
    # Very low pollution
    if highway in {"footway", "cycleway", "path"}:
        return 0.1
    
    return 0.3  # fallback

# Compute surface quality score
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
    
    return 0.5  # fallback

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
    for u, v, key, data in graph.edges(keys=True, data=True):
        data["distance"] = data.get("length", 1)
        data["lighting"] = extract_lighting(data)
        data["greenery"] = extract_greenery(data, graph, u, v)
        data["pollution"] = extract_pollution(data)
        data["surface_quality"] = extract_surface_quality(data)
    return graph