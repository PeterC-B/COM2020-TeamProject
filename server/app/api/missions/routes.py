from flask import Blueprint, request
from app.api.responses import ok, created
from flask_jwt_extended import current_user, jwt_required
from app.domain.missions.missions_read import MissionReadSchema
from app.domain.missions.mission_progress_read import MissionProgressReadSchema
from app.domain.errors import NotFoundError

def create_missions_blueprint(
    list_missions_uc,
    get_mission_uc,
    get_mission_progress_uc, 
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
    @jwt_required()
    def get_mission(mission_id):
        try:
            mission = get_mission_uc.execute(mission_id)
            mission_data = MissionReadSchema().dump(mission)

            try:
                progress = get_mission_progress_uc.execute(current_user.user_id, mission_id)
                progress_data = MissionProgressReadSchema().dump(progress)
            except NotFoundError:
                progress_data = {}

            return ok(data={**mission_data, **progress_data})

        except Exception as e:
            print("MISSION ERROR:", type(e), e)
            raise

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