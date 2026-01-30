# ORM model representation of a user in the database
import uuid

from sqlalchemy import UUID, String
from sqlalchemy import Enum as SQLEnum
from server.app.models.enums.MISSION_TIER import MissionTier
from sqlalchemy.orm import Mapped, mapped_column

from server.app.extensions import db

class MissionsModel(db.Model):
    __tablename__ = "missions"

    mission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_name: Mapped[str] = mapped_column(String(), nullable=False)
    question: Mapped[str] = mapped_column(String(), nullable=False)
    answer: Mapped[str] = mapped_column(String(), nullable=False)
    tier: Mapped[MissionTier] = mapped_column(SQLEnum(MissionTier), nullable=False)