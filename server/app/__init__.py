# Create_app() function to initialize the Flask application

from pathlib import Path

from flask import Flask
from flask_cors import CORS

from app.api.error_handlers import register_error_handlers
from app.api.graph.graph_endpoints import create_graph_route_blueprint
from app.api.health.health_endpoints import create_health_routes
from app.api.missions.routes import create_missions_blueprint
from app.api.routing.routing_endpoints import create_routing_route_blueprint
from app.api.users.routes import create_user_route_blueprint
from app.api.leaderboard.routes import create_leaderboard_blueprint
from app.config import Config
from app.extensions import db, jwt, ma, migrate
from app.repositories.graph_data_repository import GraphDataRepository
from app.repositories.mission_repository import MissionsRepository
from app.repositories.routing_graph_repository import RoutingGraphRepository
from app.repositories.leaderboard_repository import LeaderboardRepository
from app.repositories.route_query_repository import RouteQueryRepository
from app.repositories.user_repository import UserRepository
from app.use_cases.route_queries.list_route_queries import ListRouteQueries
from app.use_cases.route_queries.log_route_query import LogRouteQuery
from app.use_cases.users.forgot_password import ForgotPassword
from app.use_cases.missions.delete_mission import DeleteMission
from app.use_cases.leaderboard.get_leaderboard import GetLeaderboard
from app.use_cases.leaderboard.save_mission_progress import SaveMissionProgress
from app.use_cases.leaderboard.get_mission_progress import GetMissionProgress
from app.use_cases.graph.get_graph_data import GetGraphData
from app.use_cases.graph.get_graph_data_for_coords import FetchDataForCoordinates
from app.use_cases.graph.fetch_node_data import FetchNodeData
from app.use_cases.graph.fetch_node_context import FetchNodeContext
from app.use_cases.graph.fetch_edge_data import FetchEdgeData
from app.use_cases.graph.fetch_location_name import FetchLocationName
from app.use_cases.health.explain_edge_cost import ExplainEdgeCost
from app.use_cases.health.get_attributes import GetHealthAttributes
from app.use_cases.health.get_default_weights import GetDefaultWeights
from app.use_cases.missions.create_mission import CreateMission
from app.use_cases.missions.get_mission import GetMission
from app.use_cases.missions.list_missions import ListMissions
from app.use_cases.routing.route_yens import RouteYens
from app.use_cases.users.list_users import ListUsers
from app.use_cases.users.login_user import LoginUser
from app.use_cases.users.register_user import RegisterUser
from app.use_cases.missions.update_mission import UpdateMission
from app.models.change_logging import init_change_logging
from app.unit_of_work.sqlalchemy_uow import SqlAlchemyUnitOfWork


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
    from app.models import (
        edges_model,
        location_model,
        mission_progress_model,
        missions_model,
        nodes_model,
        user_account_model,
        route_query_model
    )
    init_change_logging()

    # Initialise the services
    session = db.session
    uow = SqlAlchemyUnitOfWork(session)


    # Initialise the Repositories
    user_repo = UserRepository(session)
    graph_data_repo = GraphDataRepository(session)
    routing_graph_repo = RoutingGraphRepository(session)
    missions_repo = MissionsRepository(session)
    leaderboard_repo = LeaderboardRepository(session)
    route_query_repo = RouteQueryRepository(session)

    # Initialise the Use Cases
    register_user_uc = RegisterUser(uow, user_repo)
    list_users_uc = ListUsers(user_repo)
    login_user_uc = LoginUser(user_repo)
    forgot_password_uc = ForgotPassword(uow, user_repo)
    get_graph_data_uc = GetGraphData(graph_data_repo)
    get_graph_data_from_coords_uc = FetchDataForCoordinates(uow, graph_data_repo)
    fetch_node_data_uc = FetchNodeData(graph_data_repo)
    fetch_node_context_uc = FetchNodeContext(graph_data_repo)
    fetch_edge_data_uc = FetchEdgeData(graph_data_repo)
    fetch_location_name_uc = FetchLocationName(graph_data_repo)
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
    log_route_query_uc = LogRouteQuery(uow, route_query_repo)
    list_route_queries_uc = ListRouteQueries(route_query_repo)

    # Initialise the Routes
    app.register_blueprint(create_user_route_blueprint(register_user_uc, list_users_uc, login_user_uc, forgot_password_uc))
    app.register_blueprint(create_graph_route_blueprint(get_graph_data_uc, get_graph_data_from_coords_uc, fetch_node_data_uc, fetch_edge_data_uc, fetch_location_name_uc, fetch_node_context_uc))
    app.register_blueprint(create_health_routes(get_health_attributes_uc, get_default_weights_uc, explain_edge_cost_uc))
    app.register_blueprint(create_missions_blueprint(list_missions_uc, get_mission_uc, create_mission_uc, update_mission_uc, delete_mission_uc))
    app.register_blueprint(create_leaderboard_blueprint(get_leaderboard_uc, get_mission_progress_uc, save_mission_progress_uc))
    app.register_blueprint(create_routing_route_blueprint(route_yens_uc, log_route_query_uc, list_route_queries_uc)
)


    # Import error handlers
    register_error_handlers(app)

    return app
