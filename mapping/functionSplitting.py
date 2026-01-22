import osmnx as ox
import geopandas as gpd

def addDistanceToDrinkingPlace(edges_gdf : gpd.GeoDataFrame, coords : tuple) -> gpd.GeoDataFrame:
    '''
    A function that returns a heatmap of where roads are close to places that allow people to drink
    
    :param edges_gdf: The GeoDataFrame that contains the edges in the chosen map
    :type edges_gdf: gpd.GeoDataFrame
    :param coords: The centre coordinates for the chosen area
    :type coords: tuple
    :return: The graph where edges are coloured based on their proximity to a place of drink
    :rtype: GeoDataFrame
    '''
    amenities = ox.features_from_point(
        coords,
        tags={"amenity":[
                "bar", "biergarten", "pub", "casino", "nightclub", "gambling"
            ]},
        dist=450
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