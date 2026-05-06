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
    for table_name, column_name in (
        ("user_profiles", "created_at"),
        ("user_profiles", "updated_at"),
        ("trip_requests", "created_at"),
        ("trip_requests", "updated_at"),
        ("recommendation_runs", "created_at"),
        ("route_plans", "created_at"),
        ("feedback_entries", "created_at"),
        ("decision_logs", "created_at"),
        ("decision_logs", "updated_at"),
    ):
        _set_timestamp_default_if_column_exists(table_name, column_name)


def downgrade() -> None:
    pass


def _set_timestamp_default_if_column_exists(table_name: str, column_name: str) -> None:
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = '{table_name}'
                  AND column_name = '{column_name}'
            ) THEN
                EXECUTE 'ALTER TABLE {table_name} ALTER COLUMN {column_name} SET DEFAULT now()';
            END IF;
        END
        $$;
        """
    )
