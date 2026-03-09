"""Routing API endpoint for Yen's algorithm."""

from flask import Blueprint, request
from server.app.schemas.route_query_schema import RouteQuerySchema
from server.app.extensions import login_required, admin_required
from flask_jwt_extended import current_user

from server.app.api.responses import ok
from server.app.schemas.route_query_schema import RouteQuerySchema
from server.app.extensions import login_required, admin_required
from server.app.api.error_handlers import ValidationError

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
            result = list_route_queries_uc.execute()
            data = [
                {
                    "query_id": rq.query_id,
                    "user_id": rq.user_id,
                    "start": rq.start,
                    "end": rq.end,
                    "weights_json": rq.weights_json,
                    "chosen_route_rank": rq.chosen_route_rank,
                    "chosen_route_path": rq.chosen_route_path,
                    "timestamp": rq.timestamp,
                    "name": user.username if user else None,
                }
                for rq, user in result
            ]
            return ok(data=data)
        except Exception as e:
            raise(ValidationError(message=e))

    return bp
