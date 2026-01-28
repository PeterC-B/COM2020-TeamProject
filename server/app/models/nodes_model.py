# ORM model representation of a user in the database
from sqlalchemy import Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db

class NodesModel(db.Model):
    __tablename__= 'nodes'

    node_id: Mapped[int] = mapped_column(Integer(), nullable=False, primary_key=True)
    x_coordinate: Mapped[float] = mapped_column(Float(15), nullable=False)
    y_coordinate: Mapped[float] = mapped_column(Float(15), nullable=False)