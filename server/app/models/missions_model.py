# ORM model representation of a user in the database
import uuid

from server.app.extensions import db
from server.app.models.enums.MISSION_TIER import MissionTier
from sqlalchemy import UUID
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

# TODO: Whenever changed, edit the report documentation


class MissionsModel(db.Model):
    __tablename__ = "missions"

    mission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_name: Mapped[str] = mapped_column(String(), nullable=False)
    question: Mapped[str] = mapped_column(String(), nullable=False)

    # Seperate answers with commas
    possible_answers: Mapped[str] = mapped_column(String(), nullable=False)
    
    # Correct answer from possible_answers
    answer: Mapped[str] = mapped_column(String(), nullable=False)
    tier: Mapped[MissionTier] = mapped_column(SQLEnum(MissionTier), nullable=False, default=MissionTier.MEDIUM)