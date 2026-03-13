"""Routing API endpoint for Yen's algorithm."""

import json

from app.api.responses import ok
from flask import Blueprint, request
from app.schemas.route_query_schema import RouteQuerySchema
from app.extensions import login_required, admin_required
from flask_jwt_extended import current_user

from app.api.responses import ok
from app.schemas.route_query_schema import RouteQuerySchema
from app.extensions import login_required, admin_required
from app.api.error_handlers import ValidationError

def create_routing_route_blueprint(route_yens_uc, log_route_query_uc, list_route_queries_uc):
    bp = Blueprint("routing", __name__, url_prefix="/api/routing")

    @bp.route("", methods=["POST"])
    def route_yens():
        try:
            data = request.get_json(silent=True) or {}

            payload, status = route_yens_uc.execute(data)

            start = data.get("start")
            end = data.get("end")
            weights = data.get("weights") or {}

            routes = payload.get("routes", [])
            chosen = routes[0] if routes else None

            chosen_route_rank = chosen["metadata"].get("rank", 1)
            chosen_route_path = chosen["path"]

            user_id = data.get("user_id")

            log_route_query_uc.execute(
                user_id=user_id,
                start=str(start),
                end=str(end),
                weights_json=weights,
                chosen_route_rank=chosen_route_rank,
                chosen_route_path=chosen_route_path,
            )

            return ok(data=payload, status=status)
        except Exception as e:
            print(f"Error: {e}")
            raise(ValidationError(message=e))

    @bp.route("/queries", methods=["GET"])
    def list_route_queries():
        try:
            rows = list_route_queries_uc.execute()

            def normalize_coord(coord):
                if isinstance(coord, list) and len(coord) == 2:
                    lat, lon = coord
                    return f"{float(lat):.6f},{float(lon):.6f}"

                if isinstance(coord, dict) and "lat" in coord and "lon" in coord:
                    return f"{float(coord['lat']):.6f},{float(coord['lon']):.6f}"

                if isinstance(coord, str):
                    cleaned = coord.strip().replace("[", "").replace("]", "")
                    parts = cleaned.split(",")
                    if len(parts) != 2:
                        raise ValueError(f"Invalid coordinate format: {coord}")
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())
                    return f"{lat:.6f},{lon:.6f}"

                raise ValueError(f"Unsupported coordinate type: {coord}")

            def normalize_weights(weights):
                if isinstance(weights, dict):
                    return json.dumps(weights, sort_keys=True)

                if weights is None:
                    return "{}"

                if isinstance(weights, str):
                    try:
                        parsed = json.loads(weights)
                        if isinstance(parsed, dict):
                            return json.dumps(parsed, sort_keys=True)
                    except:
                        pass

                try:
                    return json.dumps(weights, sort_keys=True)
                except:
                    return "{}"

            grouped = {}

            for rq, user in rows:
                start_norm = normalize_coord(rq.start)
                end_norm = normalize_coord(rq.end)
                weights_norm = normalize_weights(rq.weights_json)

                key = (start_norm, end_norm, weights_norm, ",".join(map(str, rq.chosen_route_path)))

                if key not in grouped:
                    grouped[key] = {
                        "start": rq.start,
                        "end": rq.end,
                        "weights_json": rq.weights_json,
                        "chosen_route_path": rq.chosen_route_path,
                        "timestamp": rq.timestamp,
                        "popularity": 1,
                        "name": user.username if user else None,
                    }
                else:
                    grouped[key]["popularity"] += 1
                    if rq.timestamp > grouped[key]["timestamp"]:
                        grouped[key]["timestamp"] = rq.timestamp

            data = list(grouped.values())
            data.sort(key=lambda x: x["popularity"], reverse=True)

            return ok(data=data)

        except Exception as e:
            print("ROUTE QUERY ERROR:", e)
            raise e


    return bp
