# ORM model representation of a user in the database
from sqlalchemy import Float, BigInteger
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from server.app.models.enums.HIGHWAY_FEATURES import HighwayFeatures

from server.app.extensions import db

# TODO: Whenever changed, edit the report documentation

class NodesModel(db.Model):
    __tablename__= 'nodes'

    node_id: Mapped[int] = mapped_column(BigInteger(), nullable=False, primary_key=True)
    x_coordinate: Mapped[float] = mapped_column(Float(15), nullable=False)
    y_coordinate: Mapped[float] = mapped_column(Float(15), nullable=False)

    feature: Mapped[HighwayFeatures] = mapped_column(SQLEnum(HighwayFeatures), nullable=True)