# ORM model representation of a user in the database
import uuid
from datetime import datetime

from server.app.extensions import db
from server.app.models.enums.ACCESS_TYPE import UserAccessType
from sqlalchemy import UUID, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

# TODO: Whenever changed, edit the report documentation

class UserAccountModel(db.Model):
    __tablename__ = 'user_account'

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserAccessType] = mapped_column(SQLEnum(UserAccessType), nullable=False, default=UserAccessType.TRAVELLERS)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, default=datetime.now)
    reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reset_token_expiry: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
