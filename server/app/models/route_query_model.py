# ORM model representation of a user in the database
from server.app.extensions import db
from sqlalchemy import UUID, ForeignKey, Integer, JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from server.app.models.user_account_model import UserAccountModel
from server.app.models.nodes_model import NodesModel
from datetime import datetime

# TODO: Whenever changed, edit the report documentation

class RouteQuery(db.Model):
    __tablename__= 'route_queries'

    query_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_account.user_id"), nullable=False)
    user: Mapped["UserAccountModel"] = relationship("UserAccountModel", foreign_keys=[user_id])

    start: Mapped[str] = mapped_column(String(), nullable=False)

    end: Mapped[str] = mapped_column(String(), nullable=False)
    
    weights_json: Mapped[JSON] = mapped_column(JSON(), nullable=False)

    chosen_route_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    chosen_route_path: Mapped[JSON] = mapped_column(JSON(), nullable=False)

    timestamp: Mapped[datetime] = mapped_column(DateTime(), nullable=False, default=datetime.now)

