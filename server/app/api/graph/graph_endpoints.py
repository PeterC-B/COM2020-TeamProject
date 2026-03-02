from server.app.api.responses import ok
from flask import Blueprint, request
import osmnx as ox
import requests
from server.app.api.error_handlers import ValidationError


def create_graph_route_blueprint(get_graph_data_uc, get_graph_data_from_coords_uc):
    bp = Blueprint("graph", __name__, url_prefix="/api/graph")

    @bp.route("", methods=["GET"])
    def get_graph_data():
        return ok(data=get_graph_data_uc.execute())
    
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
