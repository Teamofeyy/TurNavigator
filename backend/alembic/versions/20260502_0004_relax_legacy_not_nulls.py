"""Relax legacy not-null constraints that block the current planning model.

Revision ID: 20260502_0004
Revises: 20260502_0003
Create Date: 2026-05-02 19:45:00
"""

from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic.
revision = "20260502_0004"
down_revision = "20260502_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'user_profiles' AND column_name = 'travel_style'
            ) THEN
                EXECUTE 'ALTER TABLE user_profiles ALTER COLUMN travel_style DROP NOT NULL';
            END IF;

            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'recommendation_runs' AND column_name = 'limit_requested'
            ) THEN
                EXECUTE 'ALTER TABLE recommendation_runs ALTER COLUMN limit_requested DROP NOT NULL';
            END IF;
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'recommendation_runs' AND column_name = 'include_accommodation'
            ) THEN
                EXECUTE 'ALTER TABLE recommendation_runs ALTER COLUMN include_accommodation DROP NOT NULL';
            END IF;
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'recommendation_runs' AND column_name = 'exclude_categories'
            ) THEN
                EXECUTE 'ALTER TABLE recommendation_runs ALTER COLUMN exclude_categories DROP NOT NULL';
            END IF;
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'recommendation_runs' AND column_name = 'recommended_poi_ids'
            ) THEN
                EXECUTE 'ALTER TABLE recommendation_runs ALTER COLUMN recommended_poi_ids DROP NOT NULL';
            END IF;
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'recommendation_runs' AND column_name = 'tradeoff_summary'
            ) THEN
                EXECUTE 'ALTER TABLE recommendation_runs ALTER COLUMN tradeoff_summary DROP NOT NULL';
            END IF;

            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'feedback_entries' AND column_name = 'decision_log_id'
            ) THEN
                EXECUTE 'ALTER TABLE feedback_entries ALTER COLUMN decision_log_id DROP NOT NULL';
            END IF;
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'feedback_entries' AND column_name = 'payload'
            ) THEN
                EXECUTE 'ALTER TABLE feedback_entries ALTER COLUMN payload DROP NOT NULL';
            END IF;

            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'decision_logs' AND column_name = 'recommended_poi_ids'
            ) THEN
                EXECUTE 'ALTER TABLE decision_logs ALTER COLUMN recommended_poi_ids DROP NOT NULL';
            END IF;
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'decision_logs' AND column_name = 'explanations'
            ) THEN
                EXECUTE 'ALTER TABLE decision_logs ALTER COLUMN explanations DROP NOT NULL';
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    pass
