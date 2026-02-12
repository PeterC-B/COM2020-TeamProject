from flask import Blueprint
from server.app.api.responses import ok
from server.app.domain.missions.missions_read import MissionReadSchema


def create_missions_blueprint(list_missions_uc, get_mission_uc):
    bp = Blueprint("missions", __name__, url_prefix="/missions")

    @bp.route("", methods=["GET"])
    def list_missions():
        missions = list_missions_uc.execute()
        data = MissionReadSchema(many=True).dump(missions)
        return ok(data=data)

    @bp.route("/<uuid:mission_id>", methods=["GET"])
    def get_mission(mission_id):
        mission = get_mission_uc.execute(mission_id)
        data = MissionReadSchema().dump(mission)
        return ok(data=data)

    return bp
