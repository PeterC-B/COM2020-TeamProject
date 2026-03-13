from sqlalchemy import JSON, Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class GraphPresetModel(db.Model):
    __tablename__ = "graph_presets"

    preset_code: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    latitude: Mapped[float] = mapped_column(Float(15), nullable=False)
    longitude: Mapped[float] = mapped_column(Float(15), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    snapshot_json: Mapped[dict | None] = mapped_column(JSON(), nullable=True)
