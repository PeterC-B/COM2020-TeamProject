# ORM model representation of a user in the database
import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, String
from sqlalchemy import Enum as SQLEnum
from server.app.models.enums.ACCESS_TYPE import UserAccessType
from sqlalchemy.orm import Mapped, mapped_column

from server.app.extensions import db


class UserAccountModel(db.Model):
    __tablename__ = 'user_account'

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserAccessType] = mapped_column(SQLEnum(UserAccessType), nullable=False, default=UserAccessType.TRAVELLERS)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, default=datetime.now)