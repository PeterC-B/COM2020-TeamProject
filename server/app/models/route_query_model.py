from server.app.extensions import db
from datetime import datetime

class RouteQuery(db.Model):
    __tablename__ = "route_queries"

    query_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)

    start = db.Column(db.String, nullable=False)
    end = db.Column(db.String, nullable=False)

    weights_json = db.Column(db.JSON, nullable=False)

    chosen_route_rank = db.Column(db.Integer, nullable=False)
    chosen_route_path = db.Column(db.JSON, nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
