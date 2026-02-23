from app.api.responses import ok
from flask import Blueprint, request
import osmnx as ox


def create_graph_route_blueprint(get_graph_data_uc, get_graph_data_from_coords_uc):
    bp = Blueprint("graph", __name__, url_prefix="/api/graph")

    @bp.route("", methods=["GET"])
    def get_graph_data():
        return ok(data=get_graph_data_uc.execute())

    @bp.route("/coordinates", methods=["GET"])
    def get_graph_data_by_coords():
        location = request.args.get("location")

        if location is None:
            return {"error": "invalid location"}, 400

        lat, lon = ox.geocode(location)

        if lat is None or lon is None:
            return {"error": f"unable to find {location}'s coordinates"}, 400

        try:
            coords = (float(lat), float(lon))
        except ValueError:
            return {"error": "lat and lon are invalid"}, 400
        
        data = get_graph_data_from_coords_uc.execute(coords)

        return ok(data=data)
    
    return bp
