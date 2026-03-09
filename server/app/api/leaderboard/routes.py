from flask import Blueprint, request
from app.api.responses import ok, created
from app.domain.missions.missions_read import MissionReadSchema
from app.domain.missions.mission_progress_read import MissionProgressReadSchema


def create_leaderboard_blueprint(
    get_leaderboard_uc,
    get_mission_progress_uc,
    save_mission_progress_uc,
):
    bp = Blueprint("leaderboard", __name__, url_prefix="/api/leaderboard")
    
    @bp.route("", methods=["POST"])
    def save_mission_progress():
        try:
            save_mission_progress_uc.execute(request.get_json())
            return ok()
        except Exception as e:
            print("🔥 ERROR:", e)
            raise
    
    @bp.route("/<uuid:user_id>/<uuid:mission_id>", methods=["GET"])
    def fetch_mission_progress(mission_id, user_id):
        mission_progress = get_mission_progress_uc.execute(
            user_id,
            mission_id,
        )
        data = MissionProgressReadSchema().dump(mission_progress)
        return ok(data=data)
    
    @bp.route("", methods=["GET"])
    def get_leaderboard():
        leaderboard = get_leaderboard_uc.execute()
        data = MissionProgressReadSchema(many=True).dump(leaderboard)
        return ok(data=data)

    return bp