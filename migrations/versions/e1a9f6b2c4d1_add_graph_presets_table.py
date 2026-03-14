"""Add graph presets table

Revision ID: e1a9f6b2c4d1
Revises: 717f04694e4e
Create Date: 2026-03-12 12:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e1a9f6b2c4d1"
down_revision = "717f04694e4e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "graph_presets",
        sa.Column("preset_code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("latitude", sa.Float(precision=15), nullable=False),
        sa.Column("longitude", sa.Float(precision=15), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("snapshot_json", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("preset_code"),
        sa.UniqueConstraint("name"),
    )


def downgrade():
    op.drop_table("graph_presets")
