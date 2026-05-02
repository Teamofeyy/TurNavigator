"""Add missing timestamp defaults to legacy planning tables.

Revision ID: 20260502_0005
Revises: 20260502_0004
Create Date: 2026-05-02 20:00:00
"""

from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic.
revision = "20260502_0005"
down_revision = "20260502_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE user_profiles ALTER COLUMN created_at SET DEFAULT now();
        ALTER TABLE user_profiles ALTER COLUMN updated_at SET DEFAULT now();
        ALTER TABLE trip_requests ALTER COLUMN created_at SET DEFAULT now();
        ALTER TABLE trip_requests ALTER COLUMN updated_at SET DEFAULT now();
        ALTER TABLE recommendation_runs ALTER COLUMN created_at SET DEFAULT now();
        ALTER TABLE route_plans ALTER COLUMN created_at SET DEFAULT now();
        ALTER TABLE feedback_entries ALTER COLUMN created_at SET DEFAULT now();
        ALTER TABLE decision_logs ALTER COLUMN created_at SET DEFAULT now();
        ALTER TABLE decision_logs ALTER COLUMN updated_at SET DEFAULT now();
        """
    )


def downgrade() -> None:
    pass
