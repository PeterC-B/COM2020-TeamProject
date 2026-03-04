from flask import Blueprint, request
from server.app.api.responses import ok, created
from server.app.domain.missions.missions_read import MissionReadSchema


def create_missions_blueprint(
    list_missions_uc,
    get_mission_uc,
    create_mission_uc,
    update_mission_uc,
    delete_mission_uc,
):
    bp = Blueprint("missions", __name__, url_prefix="/api/missions")

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

    @bp.route("", methods=["POST"])
    def create_mission():
        mission = create_mission_uc.execute(request.get_json())
        data = MissionReadSchema().dump(mission)
        return created(data=data)

    @bp.route("/<uuid:mission_id>", methods=["PUT"])
    def update_mission(mission_id):
        mission = update_mission_uc.execute(
            mission_id,
            request.get_json(),
        )
        data = MissionReadSchema().dump(mission)
        return ok(data=data)
    
    @bp.route("/<uuid:mission_id>", methods=["DELETE"])
    def delete_mission(mission_id):
        delete_mission_uc.execute(
            mission_id
        )
        return {"message": "Mission deleted"}, 200

    return bp