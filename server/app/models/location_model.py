import uuid

from server.app.extensions import db
from server.app.models.enums.LOCATION_TYPE import LocationType
from server.app.models.nodes_model import NodesModel
from sqlalchemy import UUID
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

# TODO: Whenever changed, edit the report documentation

class LocationModel(db.Model):
    __tablename__ = "locations"
    location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(225), nullable=False)
    node_id: Mapped[int] = mapped_column(ForeignKey("nodes.node_id"), nullable=False)
    node: Mapped["NodesModel"] = relationship("NodesModel", foreign_keys=[node_id])
    type: Mapped[LocationType] = mapped_column(SQLEnum(LocationType), nullable=False, default=LocationType.GENERAL_AMENITY)
    information: Mapped[str] = mapped_column(String(), nullable=True)
    in_use: Mapped[bool] = mapped_column(Boolean(), nullable=False)
