from app.api.responses import ok
from flask import Blueprint, request
import osmnx as ox
import requests
from app.api.error_handlers import ValidationError, NotFoundError


def create_graph_route_blueprint(get_graph_data_uc, get_graph_data_from_coords_uc, fetch_node_data, fetch_edge_data, fetch_location_name):
    bp = Blueprint("graph", __name__, url_prefix="/api/graph")

    @bp.route("", methods=["GET"])
    def get_graph_data():
        try:
            return ok(data=get_graph_data_uc.execute())
        except Exception as e:
            print(f"Error: {e}")
            raise ValidationError()
    
    @bp.route("/node", methods=["GET"])
    def get_node_data():
        node_id = request.args.get("node_id")
        return ok(data=fetch_node_data.execute(node_id))
    
    @bp.route("/edge", methods=["GET"])
    def get_edge_data():
        edge_id = request.args.get("edge_id")
        return ok(data=fetch_edge_data.execute(edge_id))
    
    @bp.route("/coordinates", methods=["GET"])
    def get_graph_data_by_coords():
        try:
            location = request.args.get("location")

            if location is None:
                return ValidationError(message="Unable to fetch location")

            lat, lon = ox.geocode(location)

            if lat is None or lon is None:
                return ValidationError(message="Unable to fetch location")

            try:
                coords = (float(lat), float(lon))
            except ValueError:
                return {"error": "lat and lon are invalid"}, 400
            
            data = get_graph_data_from_coords_uc.execute(coords)
            return ok(data=data)
        except Exception as e:
            print("Error:", e)
            raise

    @bp.route("/location/name", methods=["GET"])
    def get_location_name():
        node_id = request.args.get("node_id")
        if node_id is None:
            raise NotFoundError(message="Node ID is missing")
        data = fetch_location_name.execute(node_id)
        return ok(data=data)
        
    
    @bp.route("/locations", methods=["GET"])
    def get_like_locations():
        query = request.args.get("like_string")

        if not query:
            return
        
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": query,
                "format": "json",
                "addressdetails": 1,
                "limit": 5,
                "countrycodes": "gb",
                "featuretype" : "city",
            },
            headers={
                "User-Agent": "your-app-name"
            }
        )

        results = response.json()

        results.sort(key=lambda x : x.get("importance", 0), reverse=True)

        suggestions = [
            {
                "display_name": r["display_name"],
                "lat": r["lat"],
                "lon": r["lon"],
            }
            for r in results
        ]

        return ok(data=suggestions)
    
    return bp
