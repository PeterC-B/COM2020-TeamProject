# ORM model representation of a user in the database
from server.app.extensions import db
from server.app.models.nodes_model import NodesModel
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

# TODO: Whenever changed, edit the report documentation

class EdgesModel(db.Model):
    '''
    Docstring for EdgesModel
    '''
    __tablename__ = "edges"

    edge_id: Mapped[int] = mapped_column(Integer(), nullable=False, primary_key=True)

    from_node_id: Mapped[int] = mapped_column(ForeignKey("nodes.node_id"), nullable=False)
    to_node_id: Mapped[int] = mapped_column(ForeignKey("nodes.node_id"), nullable=False)

    from_node: Mapped["NodesModel"] = relationship("NodesModel", foreign_keys=[from_node_id])
    to_node: Mapped["NodesModel"] = relationship("NodesModel", foreign_keys=[to_node_id])

    key: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    length: Mapped[float] = mapped_column(Float(), nullable=False)
    travel_time: Mapped[float] = mapped_column(Float(), nullable=False)
    access_score: Mapped[float] = mapped_column(Float(), nullable=False)
    
    geometry: Mapped[str] = mapped_column(String(), nullable=False)

    lighting: Mapped[float] = mapped_column(Float(), nullable=False)
    greenery: Mapped[float] = mapped_column(Float(), nullable=False)
    pollution: Mapped[float] = mapped_column(Float(), nullable=False)
    surface_quality: Mapped[float] = mapped_column(Float(), nullable=False)