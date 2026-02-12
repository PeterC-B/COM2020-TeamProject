"""
Analytics utilities for converting node/edge GeoDataFrames
into clean tabular formats for admin dashboards and reports.
"""

def create_nodes_table(nodes_gdf):
    nodes_table = nodes_gdf.reset_index()[["osmid", "x", "y"]]
    nodes_table = nodes_table.rename(columns={"osmid": "node_id"})
    return nodes_table


def create_edges_table(edges_gdf):
    edges_table = edges_gdf.reset_index()[[
        "u", "v", "key",
        "length",
        "travel_time",
        "access_score",
    ]]

    edges_table = edges_table.rename(columns={
        "u": "from_node",
        "v": "to_node",
    })

    return edges_table