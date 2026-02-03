import uuid

from sqlalchemy import UUID, ForeignKey, Integer
from sqlalchemy import Enum as SQLEnum
from server.app.models.missions_model import MissionsModel
from server.app.models.user_account_model import UserAccountModel
from server.app.models.enums.MISSION_STATUS import MissionStatus
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.extensions import db

class MissionProgressModel(db.Model):
    __tablename__ = "mission_progress"
    mission_progress_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_account.user_id"), nullable=False)
    user: Mapped["UserAccountModel"] = relationship("UserAccountModel", foreign_keys=[user_id])

    mission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("missions.mission_id"), nullable=False)
    mission: Mapped["MissionsModel"] = relationship("MissionsModel", foreign_keys=[mission_id])

    status: Mapped[MissionStatus] = mapped_column(SQLEnum(MissionStatus), nullable=False, default=MissionStatus.NOT_STARTED)
    score: Mapped[int] = mapped_column(Integer(), nullable=False)