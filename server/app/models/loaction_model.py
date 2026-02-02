import uuid
from sqlalchemy import Float, Integer, UUID, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from server.app.models.nodes_model import NodesModel
from server.app.extensions import db

class LocationModel(db.Model):
    __tablename__ = "locations"
    location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    node_id: Mapped[int] = mapped_column(ForeignKey("nodes.node_id"), nullable=False)
    node: Mapped["NodesModel"] = relationship("NodesModel", foreign_keys=[node_id])
