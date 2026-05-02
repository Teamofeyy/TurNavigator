"""Fix profile schema mismatches and add profile names.

Revision ID: 20260502_0003
Revises: 20260502_0002
Create Date: 2026-05-02 18:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260502_0003"
down_revision = ("20260502_0002", "20260502_0001")
branch_labels = None
depends_on = None


PROFILE_NAME_DEFAULT = "Профиль путешественника"


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE user_profiles
        ADD COLUMN IF NOT EXISTS profile_name VARCHAR(120);
        """
    )
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'user_profiles'
                  AND column_name = 'title'
            ) THEN
                EXECUTE $sql$
                    UPDATE user_profiles
                    SET profile_name = COALESCE(
                        NULLIF(profile_name, ''),
                        NULLIF(title, ''),
                        '{PROFILE_NAME_DEFAULT}'
                    )
                $sql$;
            ELSE
                EXECUTE $sql$
                    UPDATE user_profiles
                    SET profile_name = COALESCE(NULLIF(profile_name, ''), '{PROFILE_NAME_DEFAULT}')
                $sql$;
            END IF;
        END $$;
        """
    )
    op.alter_column(
        "user_profiles",
        "profile_name",
        existing_type=sa.String(length=120),
        nullable=False,
        server_default=PROFILE_NAME_DEFAULT,
    )
    op.execute(
        """
        DO $$
        DECLARE
            trust_level_type text;
        BEGIN
            SELECT data_type
            INTO trust_level_type
            FROM information_schema.columns
            WHERE table_name = 'user_profiles'
              AND column_name = 'trust_level';

            IF trust_level_type = 'double precision' THEN
                EXECUTE $sql$
                    ALTER TABLE user_profiles
                    ALTER COLUMN trust_level TYPE VARCHAR(16)
                    USING (
                        CASE
                            WHEN trust_level IS NULL THEN 'medium'
                            WHEN trust_level >= 0.75 THEN 'high'
                            WHEN trust_level >= 0.35 THEN 'medium'
                            ELSE 'low'
                        END
                    )
                $sql$;
            ELSIF trust_level_type IS NOT NULL AND trust_level_type <> 'character varying' THEN
                EXECUTE $sql$
                    ALTER TABLE user_profiles
                    ALTER COLUMN trust_level TYPE VARCHAR(16)
                    USING COALESCE(trust_level::text, 'medium')
                $sql$;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        ALTER TABLE trip_requests
        ADD COLUMN IF NOT EXISTS start_location JSONB,
        ADD COLUMN IF NOT EXISTS end_location JSONB,
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

        ALTER TABLE recommendation_runs
        ADD COLUMN IF NOT EXISTS request_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
        ADD COLUMN IF NOT EXISTS recommendations JSONB NOT NULL DEFAULT '[]'::jsonb;

        ALTER TABLE route_plans
        ADD COLUMN IF NOT EXISTS route_points JSONB NOT NULL DEFAULT '[]'::jsonb,
        ADD COLUMN IF NOT EXISTS start_location JSONB,
        ADD COLUMN IF NOT EXISTS end_location JSONB,
        ADD COLUMN IF NOT EXISTS return_leg_distance_km DOUBLE PRECISION NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS return_leg_travel_minutes INTEGER NOT NULL DEFAULT 0;

        ALTER TABLE feedback_entries
        ADD COLUMN IF NOT EXISTS route_id INTEGER,
        ADD COLUMN IF NOT EXISTS city_id INTEGER,
        ADD COLUMN IF NOT EXISTS route_points_count INTEGER NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS estimated_budget INTEGER NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS total_time_minutes INTEGER NOT NULL DEFAULT 0;

        ALTER TABLE decision_logs
        ADD COLUMN IF NOT EXISTS event_type VARCHAR(64) NOT NULL DEFAULT 'legacy_import',
        ADD COLUMN IF NOT EXISTS city_id INTEGER NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS route_id INTEGER,
        ADD COLUMN IF NOT EXISTS feedback_id INTEGER,
        ADD COLUMN IF NOT EXISTS recommendations_snapshot JSONB,
        ADD COLUMN IF NOT EXISTS explanation_snapshot JSONB,
        ADD COLUMN IF NOT EXISTS feedback_snapshot JSONB;
        """
    )
    op.execute(
        """
        UPDATE recommendation_runs
        SET request_snapshot = COALESCE(request_snapshot, '{}'::jsonb),
            recommendations = COALESCE(recommendations, '[]'::jsonb);

        UPDATE feedback_entries AS feedback
        SET city_id = route.city_id,
            estimated_budget = route.estimated_budget,
            total_time_minutes = route.total_time_minutes
        FROM route_plans AS route
        WHERE feedback.route_id = route.id
          AND (
              feedback.city_id IS NULL
              OR feedback.estimated_budget = 0
              OR feedback.total_time_minutes = 0
          );
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'feedback_entries'
                  AND column_name = 'route_plan_id'
            ) THEN
                EXECUTE $sql$
                    UPDATE feedback_entries
                    SET route_id = COALESCE(route_id, route_plan_id)
                    WHERE route_id IS NULL
                $sql$;
            END IF;

            EXECUTE $sql$
                UPDATE feedback_entries AS feedback
                SET city_id = route.city_id,
                    estimated_budget = route.estimated_budget,
                    total_time_minutes = route.total_time_minutes
                FROM route_plans AS route
                WHERE feedback.route_id = route.id
                  AND (
                      feedback.city_id IS NULL
                      OR feedback.estimated_budget = 0
                      OR feedback.total_time_minutes = 0
                  )
            $sql$;

            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'decision_logs'
                  AND column_name = 'route_plan_id'
            ) THEN
                EXECUTE $sql$
                    UPDATE decision_logs
                    SET route_id = COALESCE(route_id, route_plan_id)
                    WHERE route_id IS NULL
                $sql$;
            END IF;

            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'feedback_entries'
                  AND column_name = 'decision_log_id'
            ) THEN
                EXECUTE $sql$
                    UPDATE decision_logs AS log_entry
                    SET feedback_id = feedback.id
                    FROM feedback_entries AS feedback
                    WHERE feedback.decision_log_id = log_entry.id
                      AND log_entry.feedback_id IS NULL
                $sql$;
            END IF;

            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'decision_logs'
                  AND column_name = 'recommended_poi_ids'
            ) THEN
                EXECUTE $sql$
                    UPDATE decision_logs
                    SET recommendations_snapshot = COALESCE(
                        recommendations_snapshot,
                        to_jsonb(recommended_poi_ids)
                    )
                    WHERE recommended_poi_ids IS NOT NULL
                $sql$;
            END IF;

            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'decision_logs'
                  AND column_name = 'explanations'
            ) THEN
                EXECUTE $sql$
                    UPDATE decision_logs
                    SET explanation_snapshot = COALESCE(
                        explanation_snapshot,
                        to_jsonb(explanations)
                    )
                    WHERE explanations IS NOT NULL
                $sql$;
            END IF;

            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'decision_logs'
                  AND column_name = 'feedback'
            ) THEN
                EXECUTE $sql$
                    UPDATE decision_logs
                    SET feedback_snapshot = COALESCE(
                        feedback_snapshot,
                        to_jsonb(feedback)
                    )
                    WHERE feedback IS NOT NULL
                $sql$;
            END IF;

            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'decision_logs'
                  AND column_name = 'route_plan_id'
            ) THEN
                EXECUTE $sql$
                    UPDATE decision_logs AS log_entry
                    SET city_id = COALESCE(NULLIF(log_entry.city_id, 0), trip.city_id, 0)
                    FROM trip_requests AS trip
                    WHERE trip.id = log_entry.trip_request_id
                $sql$;
                EXECUTE $sql$
                    UPDATE decision_logs AS log_entry
                    SET city_id = COALESCE(NULLIF(log_entry.city_id, 0), route.city_id, 0)
                    FROM route_plans AS route
                    WHERE route.id = COALESCE(log_entry.route_id, log_entry.route_plan_id)
                $sql$;
            ELSE
                EXECUTE $sql$
                    UPDATE decision_logs AS log_entry
                    SET city_id = COALESCE(NULLIF(log_entry.city_id, 0), trip.city_id, 0)
                    FROM trip_requests AS trip
                    WHERE trip.id = log_entry.trip_request_id
                $sql$;
                EXECUTE $sql$
                    UPDATE decision_logs AS log_entry
                    SET city_id = COALESCE(NULLIF(log_entry.city_id, 0), route.city_id, 0)
                    FROM route_plans AS route
                    WHERE route.id = log_entry.route_id
                $sql$;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE user_profiles
        ALTER COLUMN trust_level TYPE DOUBLE PRECISION
        USING (
            CASE trust_level
                WHEN 'high' THEN 0.85
                WHEN 'medium' THEN 0.5
                ELSE 0.15
            END
        );
        """
    )
    op.execute(
        """
        ALTER TABLE user_profiles
        DROP COLUMN IF EXISTS profile_name;
        """
    )
