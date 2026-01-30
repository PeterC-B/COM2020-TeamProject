from server.app.models.Base import Base
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(model_class=Base)

migrate = Migrate()

jwt = JWTManager()

ma = Marshmallow()