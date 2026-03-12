import requests
from app.api.error_handlers import NotFoundError, ValidationError
from app.api.responses import ok
from flask import Blueprint, request


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
            lat_arg = request.args.get("lat")
            lon_arg = request.args.get("lon")

            print("Received parameters - coords:", lat_arg, "lon:", lon_arg)

            if lat_arg is not None and lon_arg is not None:
                lat, lon = lat_arg, lon_arg
            else:
                return ValidationError(message="Provide either location or lat/lon")

            try:
                coords = (float(lat), float(lon))
            except ValueError:
                return {"error": "lat and lon are invalid"}, 400

            # return ok(data={"message": "Received coordinates", "lat": lat, "lon": lon})
            
            data = get_graph_data_from_coords_uc.execute(coords)
            return ok(data=data)
        except Exception as e:
            print("Error:", e)
            raise

    @bp.route("/location/name", methods=["GET"])
    def get_location_name():
        node_id_arg = request.args.get("node_id")
        if node_id_arg is None:
            raise NotFoundError(message="Node ID is missing")
        try:
            node_id = int(node_id_arg)
        except (TypeError, ValueError):
            raise ValidationError(message="node_id must be an integer")
        data = fetch_location_name.execute(node_id)
        return ok(data=data)
        
    
    # Route to return the top 5 location suggestions based on a like string query
    @bp.route("/locations", methods=["GET"])
    def get_like_locations():
        query = request.args.get("like_string")

        if not query:
            return ValidationError(message="like_string query parameter is required")
        
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
