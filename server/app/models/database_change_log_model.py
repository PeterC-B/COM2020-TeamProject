import uuid
from datetime import datetime

from sqlalchemy import JSON, UUID, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


# This table will be used to log any changes made to the database.
# It will automatically trigger on any insert, update, or delete operations on the relevant tables.
class DatabaseChangeLogModel(db.Model):
    __tablename__ = "database_change_log"

    change_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)
    record_id: Mapped[str] = mapped_column(String(100), nullable=False)
    operation: Mapped[str] = mapped_column(String(16), nullable=False)
    changed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_account.user_id"),
        nullable=True,
    )
    changed_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, default=datetime.now)
    old_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
