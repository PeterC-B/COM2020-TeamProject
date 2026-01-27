# ORM model representation of a user in the database
import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db

class NodesModel(db.Model):
    __tablename__= 'nodes'

    node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    x_coordinate: Mapped[float] = mapped_column(Float())