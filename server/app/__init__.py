# Create_app() function to initialize the Flask application

from app.api.users.routes import create_user_route_blueprint
from app.config import Config
from app.extensions import db, jwt, ma, migrate
from app.repositories.user_repository import UserRepository
from app.unit_of_work.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.use_cases.users.register_user import RegisterUser
from flask import Flask
from flask_cors import CORS


def create_app():
    # Application instance
    app = Flask(__name__)

    # Load the configuration class for the app
    config = Config()
    config.get_config()

    app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI

    app.config['JWT_SECRET_KEY'] = config.SECRET_KEY

    # # Enable CORS
    # CORS(app, resources={r'/*': {'origins': config.CORS_ADDRESSES}})


    # Initialise extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)

    # Register the models
    from app.models import user_model

    # Initialise the services
    session = db.session
    uow = SqlAlchemyUnitOfWork(session)


    # Initialise the Repositories
    user_repo = UserRepository(session)

    # Initialise the Use Cases
    register_user_uc = RegisterUser(uow, user_repo)

    # Initialise the Routes
    app.register_blueprint(create_user_route_blueprint(register_user_uc))


    return app