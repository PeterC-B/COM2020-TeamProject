# ORM model representation of a user in the database
import uuid

from app.extensions import db
from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column


class UserModel(db.Model):
    __tablename__ = 'user'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)