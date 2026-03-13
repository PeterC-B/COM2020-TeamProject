import uuid

from app.extensions import db
from app.models.enums.MISSION_STATUS import MissionStatus
from app.models.missions_model import MissionsModel
from app.models.user_account_model import UserAccountModel
from sqlalchemy import UUID, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

# TODO: Whenever changed, edit the report documentation


class MissionProgressModel(db.Model):
    __tablename__ = "mission_progress"
    mission_progress_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_account.user_id"), nullable=False)
    user: Mapped["UserAccountModel"] = relationship("UserAccountModel", foreign_keys=[user_id])

    mission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("missions.mission_id"), nullable=False)
    mission: Mapped["MissionsModel"] = relationship("MissionsModel", foreign_keys=[mission_id])

    status: Mapped[MissionStatus] = mapped_column(SQLEnum(MissionStatus), nullable=False, default=MissionStatus.NOT_STARTED)
    score: Mapped[int] = mapped_column(Integer(), nullable=False)

    selected_answer: Mapped[str | None] = mapped_column(String(), nullable=True)
