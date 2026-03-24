"""Align missionstatus enum with app usage

Revision ID: 9d7b1f7df0d3
Revises: e13c6d21ecaa
Create Date: 2026-03-23 23:45:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9d7b1f7df0d3"
down_revision = "e13c6d21ecaa"
branch_labels = None
depends_on = None


OLD_VALUES = ("NOT_STARTED", "IN_PROGRESS", "COMPLETED")
NEW_VALUES = ("NOT_STARTED", "INCORRECT", "CORRECT")


def upgrade():
    op.execute("ALTER TYPE missionstatus RENAME TO missionstatus_old")
    sa.Enum(*NEW_VALUES, name="missionstatus").create(op.get_bind())

    op.execute(
        """
        ALTER TABLE mission_progress
        ALTER COLUMN status TYPE missionstatus
        USING (
            CASE status::text
                WHEN 'NOT_STARTED' THEN 'NOT_STARTED'
                WHEN 'IN_PROGRESS' THEN 'INCORRECT'
                WHEN 'COMPLETED' THEN 'CORRECT'
            END
        )::missionstatus
        """
    )

    op.execute("DROP TYPE missionstatus_old")


def downgrade():
    op.execute("ALTER TYPE missionstatus RENAME TO missionstatus_new")
    sa.Enum(*OLD_VALUES, name="missionstatus").create(op.get_bind())

    op.execute(
        """
        ALTER TABLE mission_progress
        ALTER COLUMN status TYPE missionstatus
        USING (
            CASE status::text
                WHEN 'NOT_STARTED' THEN 'NOT_STARTED'
                WHEN 'INCORRECT' THEN 'IN_PROGRESS'
                WHEN 'CORRECT' THEN 'COMPLETED'
            END
        )::missionstatus
        """
    )

    op.execute("DROP TYPE missionstatus_new")
