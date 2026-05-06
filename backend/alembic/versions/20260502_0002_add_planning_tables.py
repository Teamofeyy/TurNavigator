"""Add planning persistence tables.

Revision ID: 20260502_0002
Revises: 20260427_0001
Create Date: 2026-05-02 15:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260502_0002"
down_revision = "20260427_0001"
branch_labels = None
depends_on = None


json_type = postgresql.JSONB(astext_type=sa.Text())


def _table_exists(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in set(inspector.get_table_names())


def _index_exists(table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def _column_exists(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def upgrade() -> None:
    if not _table_exists("user_profiles"):
        op.create_table(
            "user_profiles",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("interests", json_type, nullable=False),
            sa.Column("budget_level", sa.String(length=32), nullable=False),
            sa.Column("max_budget", sa.Integer(), nullable=False),
            sa.Column("pace", sa.String(length=32), nullable=False),
            sa.Column("max_walking_distance_km", sa.Float(), nullable=False),
            sa.Column("preferred_transport", sa.String(length=32), nullable=False),
            sa.Column("explanation_level", sa.String(length=32), nullable=False),
            sa.Column("goals", json_type, nullable=False),
            sa.Column("must_have", json_type, nullable=False),
            sa.Column("avoid", json_type, nullable=False),
            sa.Column("compromise_strategy", sa.String(length=32), nullable=False),
            sa.Column("trust_level", sa.String(length=16), nullable=False),
            sa.Column("accessibility_needs", json_type, nullable=False),
            sa.Column("preferred_time_windows", json_type, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_user_profiles")),
        )

    if not _table_exists("trip_requests"):
        op.create_table(
            "trip_requests",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("city_id", sa.Integer(), nullable=False),
            sa.Column("profile_id", sa.Integer(), nullable=False),
            sa.Column("days_count", sa.Integer(), nullable=False),
            sa.Column("daily_time_limit_hours", sa.Integer(), nullable=False),
            sa.Column("selected_interests", json_type, nullable=False),
            sa.Column("constraints", json_type, nullable=False),
            sa.Column("start_location", json_type, nullable=True),
            sa.Column("end_location", json_type, nullable=True),
            sa.Column("profile_snapshot", json_type, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["profile_id"], ["user_profiles.id"], name=op.f("fk_trip_requests_profile_id_user_profiles"), ondelete="RESTRICT"),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_trip_requests")),
        )
    if _column_exists("trip_requests", "city_id") and not _index_exists("trip_requests", op.f("ix_trip_requests_city_id")):
        op.create_index(op.f("ix_trip_requests_city_id"), "trip_requests", ["city_id"], unique=False)
    if _column_exists("trip_requests", "profile_id") and not _index_exists("trip_requests", op.f("ix_trip_requests_profile_id")):
        op.create_index(op.f("ix_trip_requests_profile_id"), "trip_requests", ["profile_id"], unique=False)

    if not _table_exists("recommendation_runs"):
        op.create_table(
            "recommendation_runs",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("trip_request_id", sa.Integer(), nullable=False),
            sa.Column("city_id", sa.Integer(), nullable=False),
            sa.Column("request_snapshot", json_type, nullable=False),
            sa.Column("recommendations", json_type, nullable=False),
            sa.Column("total_candidates", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["trip_request_id"], ["trip_requests.id"], name=op.f("fk_recommendation_runs_trip_request_id_trip_requests"), ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_recommendation_runs")),
        )
    if _column_exists("recommendation_runs", "city_id") and not _index_exists("recommendation_runs", op.f("ix_recommendation_runs_city_id")):
        op.create_index(op.f("ix_recommendation_runs_city_id"), "recommendation_runs", ["city_id"], unique=False)
    if _column_exists("recommendation_runs", "trip_request_id") and not _index_exists("recommendation_runs", op.f("ix_recommendation_runs_trip_request_id")):
        op.create_index(op.f("ix_recommendation_runs_trip_request_id"), "recommendation_runs", ["trip_request_id"], unique=False)

    if not _table_exists("route_plans"):
        op.create_table(
            "route_plans",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("trip_request_id", sa.Integer(), nullable=False),
            sa.Column("recommendation_run_id", sa.Integer(), nullable=True),
            sa.Column("city_id", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("total_distance_km", sa.Float(), nullable=False),
            sa.Column("total_travel_minutes", sa.Integer(), nullable=False),
            sa.Column("total_visit_minutes", sa.Integer(), nullable=False),
            sa.Column("total_time_minutes", sa.Integer(), nullable=False),
            sa.Column("estimated_budget", sa.Integer(), nullable=False),
            sa.Column("days_count", sa.Integer(), nullable=False),
            sa.Column("daily_time_limit_minutes", sa.Integer(), nullable=False),
            sa.Column("within_time_limit", sa.Boolean(), nullable=False),
            sa.Column("within_budget", sa.Boolean(), nullable=False),
            sa.Column("skipped_poi_ids", json_type, nullable=False),
            sa.Column("route_points", json_type, nullable=False),
            sa.Column("start_location", json_type, nullable=True),
            sa.Column("end_location", json_type, nullable=True),
            sa.Column("return_leg_distance_km", sa.Float(), nullable=False),
            sa.Column("return_leg_travel_minutes", sa.Integer(), nullable=False),
            sa.Column("explanation_summary", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["recommendation_run_id"], ["recommendation_runs.id"], name=op.f("fk_route_plans_recommendation_run_id_recommendation_runs"), ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["trip_request_id"], ["trip_requests.id"], name=op.f("fk_route_plans_trip_request_id_trip_requests"), ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_route_plans")),
        )
    if _column_exists("route_plans", "city_id") and not _index_exists("route_plans", op.f("ix_route_plans_city_id")):
        op.create_index(op.f("ix_route_plans_city_id"), "route_plans", ["city_id"], unique=False)
    if _column_exists("route_plans", "recommendation_run_id") and not _index_exists("route_plans", op.f("ix_route_plans_recommendation_run_id")):
        op.create_index(op.f("ix_route_plans_recommendation_run_id"), "route_plans", ["recommendation_run_id"], unique=False)
    if _column_exists("route_plans", "trip_request_id") and not _index_exists("route_plans", op.f("ix_route_plans_trip_request_id")):
        op.create_index(op.f("ix_route_plans_trip_request_id"), "route_plans", ["trip_request_id"], unique=False)

    if not _table_exists("feedback_entries"):
        op.create_table(
            "feedback_entries",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("route_id", sa.Integer(), nullable=False),
            sa.Column("trip_request_id", sa.Integer(), nullable=False),
            sa.Column("city_id", sa.Integer(), nullable=False),
            sa.Column("rating", sa.Integer(), nullable=False),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("route_points_count", sa.Integer(), nullable=False),
            sa.Column("estimated_budget", sa.Integer(), nullable=False),
            sa.Column("total_time_minutes", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["route_id"], ["route_plans.id"], name=op.f("fk_feedback_entries_route_id_route_plans"), ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["trip_request_id"], ["trip_requests.id"], name=op.f("fk_feedback_entries_trip_request_id_trip_requests"), ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_feedback_entries")),
        )
    if _column_exists("feedback_entries", "city_id") and not _index_exists("feedback_entries", op.f("ix_feedback_entries_city_id")):
        op.create_index(op.f("ix_feedback_entries_city_id"), "feedback_entries", ["city_id"], unique=False)
    if _column_exists("feedback_entries", "route_id") and not _index_exists("feedback_entries", op.f("ix_feedback_entries_route_id")):
        op.create_index(op.f("ix_feedback_entries_route_id"), "feedback_entries", ["route_id"], unique=False)
    if _column_exists("feedback_entries", "trip_request_id") and not _index_exists("feedback_entries", op.f("ix_feedback_entries_trip_request_id")):
        op.create_index(op.f("ix_feedback_entries_trip_request_id"), "feedback_entries", ["trip_request_id"], unique=False)

    if not _table_exists("decision_logs"):
        op.create_table(
            "decision_logs",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("event_type", sa.String(length=64), nullable=False),
            sa.Column("city_id", sa.Integer(), nullable=False),
            sa.Column("trip_request_id", sa.Integer(), nullable=True),
            sa.Column("recommendation_run_id", sa.Integer(), nullable=True),
            sa.Column("route_id", sa.Integer(), nullable=True),
            sa.Column("feedback_id", sa.Integer(), nullable=True),
            sa.Column("input_context", json_type, nullable=False),
            sa.Column("profile_snapshot", json_type, nullable=True),
            sa.Column("recommendations_snapshot", json_type, nullable=True),
            sa.Column("route_snapshot", json_type, nullable=True),
            sa.Column("explanation_snapshot", json_type, nullable=True),
            sa.Column("feedback_snapshot", json_type, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["feedback_id"], ["feedback_entries.id"], name=op.f("fk_decision_logs_feedback_id_feedback_entries"), ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["recommendation_run_id"], ["recommendation_runs.id"], name=op.f("fk_decision_logs_recommendation_run_id_recommendation_runs"), ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["route_id"], ["route_plans.id"], name=op.f("fk_decision_logs_route_id_route_plans"), ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["trip_request_id"], ["trip_requests.id"], name=op.f("fk_decision_logs_trip_request_id_trip_requests"), ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_decision_logs")),
        )
    if _column_exists("decision_logs", "city_id") and not _index_exists("decision_logs", op.f("ix_decision_logs_city_id")):
        op.create_index(op.f("ix_decision_logs_city_id"), "decision_logs", ["city_id"], unique=False)
    if _column_exists("decision_logs", "event_type") and not _index_exists("decision_logs", op.f("ix_decision_logs_event_type")):
        op.create_index(op.f("ix_decision_logs_event_type"), "decision_logs", ["event_type"], unique=False)
    if _column_exists("decision_logs", "feedback_id") and not _index_exists("decision_logs", op.f("ix_decision_logs_feedback_id")):
        op.create_index(op.f("ix_decision_logs_feedback_id"), "decision_logs", ["feedback_id"], unique=False)
    if _column_exists("decision_logs", "recommendation_run_id") and not _index_exists("decision_logs", op.f("ix_decision_logs_recommendation_run_id")):
        op.create_index(op.f("ix_decision_logs_recommendation_run_id"), "decision_logs", ["recommendation_run_id"], unique=False)
    if _column_exists("decision_logs", "route_id") and not _index_exists("decision_logs", op.f("ix_decision_logs_route_id")):
        op.create_index(op.f("ix_decision_logs_route_id"), "decision_logs", ["route_id"], unique=False)
    if _column_exists("decision_logs", "trip_request_id") and not _index_exists("decision_logs", op.f("ix_decision_logs_trip_request_id")):
        op.create_index(op.f("ix_decision_logs_trip_request_id"), "decision_logs", ["trip_request_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_decision_logs_trip_request_id"), table_name="decision_logs")
    op.drop_index(op.f("ix_decision_logs_route_id"), table_name="decision_logs")
    op.drop_index(op.f("ix_decision_logs_recommendation_run_id"), table_name="decision_logs")
    op.drop_index(op.f("ix_decision_logs_feedback_id"), table_name="decision_logs")
    op.drop_index(op.f("ix_decision_logs_event_type"), table_name="decision_logs")
    op.drop_index(op.f("ix_decision_logs_city_id"), table_name="decision_logs")
    op.drop_table("decision_logs")

    op.drop_index(op.f("ix_feedback_entries_trip_request_id"), table_name="feedback_entries")
    op.drop_index(op.f("ix_feedback_entries_route_id"), table_name="feedback_entries")
    op.drop_index(op.f("ix_feedback_entries_city_id"), table_name="feedback_entries")
    op.drop_table("feedback_entries")

    op.drop_index(op.f("ix_route_plans_trip_request_id"), table_name="route_plans")
    op.drop_index(op.f("ix_route_plans_recommendation_run_id"), table_name="route_plans")
    op.drop_index(op.f("ix_route_plans_city_id"), table_name="route_plans")
    op.drop_table("route_plans")

    op.drop_index(op.f("ix_recommendation_runs_trip_request_id"), table_name="recommendation_runs")
    op.drop_index(op.f("ix_recommendation_runs_city_id"), table_name="recommendation_runs")
    op.drop_table("recommendation_runs")

    op.drop_index(op.f("ix_trip_requests_profile_id"), table_name="trip_requests")
    op.drop_index(op.f("ix_trip_requests_city_id"), table_name="trip_requests")
    op.drop_table("trip_requests")

    op.drop_table("user_profiles")
