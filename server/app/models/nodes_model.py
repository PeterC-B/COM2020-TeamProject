# ORM model representation of a user in the database
from app.extensions import db
from sqlalchemy import BigInteger, String, Float
from sqlalchemy.orm import Mapped, mapped_column

# TODO: Whenever changed, edit the report documentation

class NodesModel(db.Model):
    __tablename__= 'nodes'

    node_id: Mapped[int] = mapped_column(BigInteger(), nullable=False, primary_key=True)
    x_coordinate: Mapped[float] = mapped_column(Float(15), nullable=False)
    y_coordinate: Mapped[float] = mapped_column(Float(15), nullable=False)

    feature: Mapped[str] = mapped_column(String(), nullable=True)