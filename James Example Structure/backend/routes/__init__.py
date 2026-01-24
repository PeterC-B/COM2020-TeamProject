"""
Register all route blueprints for the flask app
"""

from .routing_endpoints import routing_bp
from .health_endpoints import health_bp

# Attatch all blueprints to the flask app
def register_routes(app):
    app.register_blueprint(routing_bp)
    app.register_blueprint(health_bp)