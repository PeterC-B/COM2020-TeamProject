"""Routing API endpoint for Yen's algorithm."""

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
            # Fetch all (RouteQuery, UserAccountModel) pairs
            rows = list_route_queries_uc.execute()

            # Aggregate by (start, end)
            popularity_map = {}

            for rq, user in rows:
                key = (rq.start, rq.end)

                if key not in popularity_map:
                    popularity_map[key] = {
                        "start": rq.start,
                        "end": rq.end,
                        "popularity": 0,
                        "most_recent": rq.timestamp,
                        "unique_users": set(),
                    }

                popularity_map[key]["popularity"] += 1
                popularity_map[key]["unique_users"].add(rq.user_id)

                # Update most recent timestamp
                if rq.timestamp > popularity_map[key]["most_recent"]:
                    popularity_map[key]["most_recent"] = rq.timestamp

            # Flatten aggregated data
            aggregated = []
            for key, data in popularity_map.items():
                aggregated.append({
                    "start": data["start"],
                    "end": data["end"],
                    "popularity": data["popularity"],
                    "most_recent": data["most_recent"],
                    "unique_users": len(data["unique_users"]),
                })

            # Sort by popularity descending
            aggregated.sort(key=lambda x: x["popularity"], reverse=True)

            return ok(data=aggregated)

        except Exception as e:
            raise ValidationError(message=e)

    return bp
