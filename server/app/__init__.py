# Create_app() function to initialize the Flask application

from pathlib import Path

from flask import Flask
from flask_cors import CORS

from server.app.api.error_handlers import register_error_handlers
from server.app.api.graph.graph_endpoints import create_graph_route_blueprint
from server.app.api.health.health_endpoints import create_health_routes
from server.app.api.missions.routes import create_missions_blueprint
from server.app.api.routing.routing_endpoints import create_routing_route_blueprint
from server.app.api.users.routes import create_user_route_blueprint
from server.app.api.leaderboard.routes import create_leaderboard_blueprint
from server.app.config import Config
from server.app.extensions import db, jwt, ma, migrate
from server.app.repositories.graph_data_repository import GraphDataRepository
from server.app.repositories.mission_repository import MissionsRepository
from server.app.repositories.leaderboard_repository import LeaderboardRepository
from server.app.repositories.routing_graph_repository import RoutingGraphRepository
from server.app.repositories.user_repository import UserRepository
from server.app.unit_of_work.sqlalchemy_uow import SqlAlchemyUnitOfWork
from server.app.use_cases.graph.get_graph_data import GetGraphData
from server.app.use_cases.graph.get_graph_data_for_coords import FetchDataForCoordinates
from server.app.use_cases.health.explain_edge_cost import ExplainEdgeCost
from server.app.use_cases.health.get_attributes import GetHealthAttributes
from server.app.use_cases.health.get_default_weights import GetDefaultWeights
from server.app.use_cases.missions.create_mission import CreateMission
from server.app.use_cases.missions.get_mission import GetMission
from server.app.use_cases.missions.list_missions import ListMissions
from server.app.use_cases.missions.delete_mission import DeleteMission
from server.app.use_cases.leaderboard.save_mission_progress import SaveMissionProgress
from server.app.use_cases.leaderboard.get_mission_progress import GetMissionProgress
from server.app.use_cases.leaderboard.get_leaderboard import GetLeaderboard
from server.app.use_cases.routing.route_yens import RouteYens
from server.app.use_cases.users.list_users import ListUsers
from server.app.use_cases.users.login_user import LoginUser
from server.app.use_cases.users.register_user import RegisterUser
from server.app.use_cases.users.forgot_password import ForgotPassword
from server.app.use_cases.missions.update_mission import UpdateMission

def create_app():
    # Application instance
    app = Flask(__name__)

    # Load the configuration class for the app
    config = Config()
    config.get_config()

    app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI

    repo_root = Path(__file__).resolve().parents[2]
    app.config["MIGRATIONS_DIR"] = str(repo_root / "migrations")


    print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])  # Debugging line
    
    app.config['JWT_SECRET_KEY'] = config.SECRET_KEY

    # Enable CORS for local frontend-backend development across ports.

    CORS(app, origins=config.CORS_ADDRESSES)


    # Initialise extensions
    db.init_app(app)
    migrate.init_app(app, db, directory=app.config["MIGRATIONS_DIR"])
    jwt.init_app(app)
    ma.init_app(app)

    # Register the models
    from server.app.models import (
        edges_model,
        location_model,
        mission_progress_model,
        missions_model,
        nodes_model,
        user_account_model,
    )

    # Initialise the services
    session = db.session
    uow = SqlAlchemyUnitOfWork(session)


    # Initialise the Repositories
    user_repo = UserRepository(session)
    graph_data_repo = GraphDataRepository()
    routing_graph_repo = RoutingGraphRepository()
    missions_repo = MissionsRepository(session)
    leaderboard_repo = LeaderboardRepository(session)

    # Initialise the Use Cases
    register_user_uc = RegisterUser(uow, user_repo)
    list_users_uc = ListUsers(user_repo)
    login_user_uc = LoginUser(user_repo)
    forgot_password_uc = ForgotPassword(uow, user_repo)
    get_graph_data_uc = GetGraphData(graph_data_repo)
    get_graph_data_for_coords_uc = FetchDataForCoordinates(graph_data_repo)
    get_health_attributes_uc = GetHealthAttributes()
    get_default_weights_uc = GetDefaultWeights()
    explain_edge_cost_uc = ExplainEdgeCost()
    route_yens_uc = RouteYens(routing_graph_repo)
    list_missions_uc = ListMissions(missions_repo)
    get_mission_uc = GetMission(missions_repo)
    create_mission_uc = CreateMission(uow, missions_repo)
    update_mission_uc = UpdateMission(uow, missions_repo)
    delete_mission_uc = DeleteMission(uow, missions_repo)
    get_leaderboard_uc = GetLeaderboard(leaderboard_repo)
    save_mission_progress_uc = SaveMissionProgress(uow, leaderboard_repo)
    get_mission_progress_uc = GetMissionProgress(leaderboard_repo)

    # Initialise the Routes
    app.register_blueprint(create_user_route_blueprint(register_user_uc, list_users_uc, login_user_uc, forgot_password_uc))
    app.register_blueprint(create_graph_route_blueprint(get_graph_data_uc, get_graph_data_for_coords_uc))
    app.register_blueprint(create_health_routes(get_health_attributes_uc, get_default_weights_uc, explain_edge_cost_uc))
    app.register_blueprint(create_routing_route_blueprint(route_yens_uc))
    app.register_blueprint(create_missions_blueprint(list_missions_uc, get_mission_uc, create_mission_uc, update_mission_uc, delete_mission_uc))
    app.register_blueprint(create_leaderboard_blueprint(get_leaderboard_uc, get_mission_progress_uc, save_mission_progress_uc))

    # Import error handlers
    register_error_handlers(app)

    return app
