from flask import Flask
from flask_cors import CORS

from server.app.api.error_handlers import register_error_handlers
from server.app.api.users.routes import create_user_route_blueprint
from server.app.config import Config
from server.app.extensions import db, jwt, ma, migrate
from server.app.repositories.user_repository import UserRepository
from server.app.unit_of_work.sqlalchemy_uow import SqlAlchemyUnitOfWork
from server.app.use_cases.users.list_users import ListUsers
from server.app.use_cases.users.register_user import RegisterUser


def create_app():
    app = Flask(__name__)

    config = Config()
    config.get_config()

    app.config["SQLALCHEMY_DATABASE_URI"] = config.DB_URI
    app.config["JWT_SECRET_KEY"] = config.SECRET_KEY

    # Initialise extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)

    # Register models
    from server.app.models import user_account_model

    # Services
    session = db.session
    uow = SqlAlchemyUnitOfWork(session)

    # Repositories
    user_repo = UserRepository(session)

    # Use cases
    register_user_uc = RegisterUser(uow, user_repo)
    list_users_uc = ListUsers(user_repo)

    # Routes
    app.register_blueprint(
        create_user_route_blueprint(register_user_uc, list_users_uc)
    )

    # Error handlers
    register_error_handlers(app)

    return app