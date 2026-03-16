from flask import Blueprint, request
from app.api.responses import ok, created
from app.domain.missions.missions_read import MissionReadSchema
from app.domain.missions.mission_progress_read import MissionProgressReadSchema
from app.api.error_handlers import NotFoundError
from app.data.convert import build_analytics_json


def create_analytics_blueprint(
    get_mission_analytics_uc,
):
    bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")
    
    @bp.route("/missions", methods=["GET"])
    def get_mission_analytics():
        try:
            analytics = get_mission_analytics_uc.execute()
            data = build_analytics_json(analytics)
            return ok(data=data)
        except Exception as e:
            print("Error:", e)
            raise NotFoundError(message=e)

    return bp