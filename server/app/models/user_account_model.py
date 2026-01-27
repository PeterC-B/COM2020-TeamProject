# ORM model representation of a user in the database
import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from server.app.extensions import db


class UserAccountModel(db.Model):
    __tablename__ = 'user_account'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)