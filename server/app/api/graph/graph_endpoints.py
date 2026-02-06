from pathlib import Path

from flask import Blueprint, jsonify

from client.public.convert import (build_edges_geojson, build_nodes_geojson,
                                   load_edge_geometries)

DATA_PATH = Path("client/public")
NODES_CSV = DATA_PATH / "nodes_table.csv"
EDGES_CSV = DATA_PATH / "edges_table.csv"
GEOM_CSV = DATA_PATH / "edges_geometry.csv"


JSON_PATH = "server/app/api/helpers/edge_list.json"

# NODES_GDF = help_algos.nodes_csv_to_gdf()
# EDGES_GDF = help_algos.edges_csv_to_gdf()



def create_graph_route_blueprint():

    bp = Blueprint("graph", __name__, url_prefix="/graph")

    # Main endpoint to get graph data (nodes + edges)
    @bp.route("/", methods=["GET"])
    def get_graph_data():

        edge_geometries = load_edge_geometries(GEOM_CSV)
        nodes_geojson = build_nodes_geojson(NODES_CSV)
        edges_geojson = build_edges_geojson(EDGES_CSV, edge_geometries)

        all_features = {
            "nodes" : nodes_geojson,
            "edges" : edges_geojson
        }

        return jsonify({"features" : all_features})
    
    return bp
    

        
        
        
    

        
        
        
    

        
        
