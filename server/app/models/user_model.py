# ORM model representation of a user in the database
import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions.db import db


class UserModel(db.Model):
    __tablename__ = 'user'

    id: Mapped[uuid.UUID] = mapped_column(uuid.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)