import osmnx as ox
import geopandas as gpd
import mapping.functionSplitting as oxXL
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from JamesExampleStructure.backend.algorithms import dijkstra_algorithm as dijkstra
from JamesExampleStructure.backend.algorithms import astar_algorithm as astar
from JamesExampleStructure.backend.algorithms import yen_algorithm as yen
from routing import *


COORDS = (51.460498, -2.585757) # Bristol
#COORDS = (51.541533, -1.905034)
TOWN = "Bristol"
DIST = 450
TRAVEL_TYPE = "walk"
LIMIT_AMENITIES = True

allPlaces = [
    [
        "Lighting",
        {
            "lit":[
                "yes"
            ],
            "highway":[
                "street_lamp"
            ]
        },
        "yellow",
        0.4, 
        70,
    ],

    [
        "Drinking Places",
        {
            "amenity":[
                "bar", "biergarten", "pub", "casino", "nightclub", "gambling"
            ]
        },
        "red",
        0.75,
        20,
    ],

    [
        "Greenery",
        {
            "landuse":[
                "grass", "cemetery", "greenery", "forest", "allotments", "farmland",
            ],
            "amenity":[
                "grave_yard"
            ],
            "natural":[
                "scrub", "wood"
            ],
            "leisure":[
                "park"
            ]
        },
        "green",
        0.75,
        20,
    ],

    [
        "Bus Stops",
        {
            "highway": [
                "bus_stop"
            ]
        },
        "blue",
        0.75,
        20,
    ],

    [
        "Crossings and Traffic Lights",
        {
            "highway":[
                "crossing", "traffic_signals"
            ]
        },
        "#AF2EEF",
        0.75,
        20,
    ],

    [
    "Amenities",
    {
        "amenity":[
            "dentist", "doctors", "hospital", "clinic", "cinema", "library", "community_centre", "place_of_worship", "school", "cafe"
        ],
        "leisure":[
            "playground"
        ],
        "tourism":[
            "artwork"
        ]
    },
    "#43DBCE",
    0.75,
    20,
    ],   

    [
    "Low Emission Zone",
    {
        "boundary":[
            "low_emission_zone"
        ]
    },
    "#FB88FF",
    0.4,
    20,
    ], 
]

G = ox.graph_from_point(
    center_point=COORDS,
    dist=DIST,
    network_type=TRAVEL_TYPE
)

G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

fig, ax = ox.plot_graph(G, show=False, close=False)
fig.savefig(f"mapping/graphs/{TOWN}/{TOWN.lower().replace(" ", "-")}_no_pois.png", dpi=300)

#==============================

nodes_gdf, edges_gdf = ox.graph_to_gdfs(G)

edgesDict = oxXL.csv_to_dict("edges_table.csv")

#distance, shortestPath = dijkstra.dijkstra(edgesDict, 104804, 13288882110, trace=False)

nodesDict = oxXL.node_csv_to_dict("nodes_table.csv")

heuristic = astar.ehf(nodesDict, 13288882110)

#distance, shortestPath = astar.astar(edgesDict, 104804, 13288882110, heuristic, trace=False)

paths = yen.yens(edgesDict, 104804, 13288882110, 3)


for path in paths:
    print_shortest_path_graph(path, "yens", f"_{paths.index(path)+1}")

#==============================

for place in allPlaces:
    oxXL.addFeatureToGraph(G, ax, COORDS, place)

ax.legend()

fig.savefig(f"mapping/graphs/{TOWN}/{TOWN.lower().replace(" ", "-")}_pois_included.png", dpi=300)
print(f"==============================\nGraph saved to files\n==============================")

G = ox.add_edge_travel_times(G)

for u, v, k, data in G.edges(keys=True, data=True):
    data["length"] = round(data["length"], 2)
    data["travel_time"] = round(data["travel_time"], 3)

nodes_gdf, edges_gdf = ox.graph_to_gdfs(G)

#edges_gdf["midpoint"] = edges_gdf.geometry.interpolate(0.5, normalized=True)

#amenities = ox.features_from_point(
#    COORDS,
#    tags={"amenity":[
#                "bar", "biergarten", "pub", "casino", "nightclub", "gambling"
#            ]},
#    dist=450,
#)

#amenities["centroid"] = amenities.geometry.centroid

#edges_m = edges_gdf.set_geometry("midpoint").to_crs(epsg=27700)
#amenities_m = amenities.set_geometry("centroid").to_crs(epsg=27700)

#edges_m = edges_gdf.to_crs(epsg=27700)
#amenities_m = amenities.to_crs(epsg=27700)

edges_gdf = oxXL.addDistanceToDrinkingPlace(edges_gdf, COORDS)

nodes_table = nodes_gdf.reset_index()[[
    "osmid",
    "x",
    "y",
]]

nodes_table = nodes_table.rename(columns={
    "osmid" : "node_id",
})

edges_table = edges_gdf.reset_index()[[
    "u", "v", "key",
    "length",
    "travel_time",
    "access_score",
]]

edges_table = edges_table.rename(columns={
    "u":"from_node",
    "v":"to_node",
})

def score_band(d):
    if d < 0.001:
        return 1
    elif d < 0.0059:
        return 0.9
    elif d < 0.0108:
        return 0.8
    elif d < 0.0157:
        return 0.7
    elif d < 0.0206:
        return 0.6
    elif d < 0.0255:
        return 0.5
    elif d < 0.0304:
        return 0.4
    elif d < 0.0353:
        return 0.3
    elif d < 0.0402:
        return 0.2
    elif d < 0.0451:
        return 0.1
    else:
        return 0

edges_gdf["score_band"] = edges_gdf["access_score"].apply(score_band)

cmap = cm.get_cmap("RdYlGn")

edges_gdf["edge_colour"] = edges_gdf["score_band"].apply(
    lambda x: mcolors.to_hex(cmap(x))
)

fig, ax = ox.plot_graph(
    G,
    edge_color=edges_gdf["edge_colour"],
    edge_linewidth=2,
    show=False,
    close=False
)

fig.savefig(f"mapping/drinkingGraphs/fromWholeEdge.png", dpi=300)
G = ox.graph_from_gdfs(nodes_gdf, edges_gdf)
ox.save_graphml(G, filepath="bristol.graphml")

edges_table_out = edges_table.copy()    

edges_table_out.insert(0, "edge_id", range(len(edges_table_out)))

edges_table_out.to_csv("edges_table.csv", index=False)

nodes_table_out = nodes_table.copy()

nodes_table_out.to_csv("nodes_table.csv", index=False)

edges_gdf_out = edges_gdf.copy()

edges_gdf_out.to_csv("edges.csv", index=False)

edgesDict = oxXL.csv_to_dict("edges_table.csv")