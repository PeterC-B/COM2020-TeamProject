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
    "#FB95FF",
    0.4,
    20,
    ]
]

import JamesExampleStructure.backend.algorithms.dijkstra_algorithm as dijk
import routing as rt
import file_reading as fle

#rt.plot_blank_graph((51.460498, -2.585757), 450, "walk", True)
graph = rt.plot_filled_graph(allPlaces, (51.460498, -2.585757), 450, "walk", True, True)

edges_dict = fle.edge_csv_to_dict("graphs/csv/edges_table.csv")
distance, shortestRoute= dijk.dijkstra(edges_dict, 104804, 13288882110, trace=False)

print(shortestRoute)

#rt.print_shortest_path_graph(graph, shortestRoute, "graphs/csv/edges_table.csv")