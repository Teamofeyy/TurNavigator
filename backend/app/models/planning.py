from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.types import json_column_type


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        default="Профиль путешественника",
    )
    interests: Mapped[list[str]] = mapped_column(json_column_type(), nullable=False, default=list)
    budget_level: Mapped[str] = mapped_column(String(32), nullable=False, default="medium")
    max_budget: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pace: Mapped[str] = mapped_column(String(32), nullable=False, default="moderate")
    max_walking_distance_km: Mapped[float] = mapped_column(Float, nullable=False, default=8.0)
    preferred_transport: Mapped[str] = mapped_column(String(32), nullable=False, default="walking")
    explanation_level: Mapped[str] = mapped_column(String(32), nullable=False, default="detailed")
    goals: Mapped[list[str]] = mapped_column(json_column_type(), nullable=False, default=list)
    must_have: Mapped[list[str]] = mapped_column(json_column_type(), nullable=False, default=list)
    avoid: Mapped[list[str]] = mapped_column(json_column_type(), nullable=False, default=list)
    compromise_strategy: Mapped[str] = mapped_column(String(32), nullable=False, default="balanced")
    trust_level: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")
    accessibility_needs: Mapped[list[str]] = mapped_column(
        json_column_type(),
        nullable=False,
        default=list,
    )
    preferred_time_windows: Mapped[list[str]] = mapped_column(
        json_column_type(),
        nullable=False,
        default=list,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    trip_requests: Mapped[list["TripRequest"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )


class TripRequest(Base):
    __tablename__ = "trip_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    days_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    daily_time_limit_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    selected_interests: Mapped[list[str]] = mapped_column(
        json_column_type(),
        nullable=False,
        default=list,
    )
    constraints: Mapped[dict[str, str | int | float | bool]] = mapped_column(
        json_column_type(),
        nullable=False,
        default=dict,
    )
    start_location: Mapped[dict | None] = mapped_column(json_column_type(), nullable=True)
    end_location: Mapped[dict | None] = mapped_column(json_column_type(), nullable=True)
    profile_snapshot: Mapped[dict] = mapped_column(json_column_type(), nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    profile: Mapped["UserProfile"] = relationship(back_populates="trip_requests")
    recommendation_runs: Mapped[list["RecommendationRun"]] = relationship(
        back_populates="trip_request",
        cascade="all, delete-orphan",
    )
    route_plans: Mapped[list["RoutePlan"]] = relationship(
        back_populates="trip_request",
        cascade="all, delete-orphan",
    )
    feedback_entries: Mapped[list["FeedbackEntry"]] = relationship(back_populates="trip_request")
    decision_logs: Mapped[list["DecisionLog"]] = relationship(back_populates="trip_request")


class RecommendationRun(Base):
    __tablename__ = "recommendation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trip_request_id: Mapped[int] = mapped_column(
        ForeignKey("trip_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    city_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    request_snapshot: Mapped[dict] = mapped_column(json_column_type(), nullable=False, default=dict)
    recommendations: Mapped[list[dict]] = mapped_column(
        json_column_type(),
        nullable=False,
        default=list,
    )
    total_candidates: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    trip_request: Mapped["TripRequest"] = relationship(back_populates="recommendation_runs")
    route_plans: Mapped[list["RoutePlan"]] = relationship(back_populates="recommendation_run")
    decision_logs: Mapped[list["DecisionLog"]] = relationship(back_populates="recommendation_run")


class RoutePlan(Base):
    __tablename__ = "route_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trip_request_id: Mapped[int] = mapped_column(
        ForeignKey("trip_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recommendation_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("recommendation_runs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    city_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    total_distance_km: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_travel_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_visit_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_budget: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    days_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    daily_time_limit_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=480)
    within_time_limit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    within_budget: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    skipped_poi_ids: Mapped[list[int]] = mapped_column(json_column_type(), nullable=False, default=list)
    route_points: Mapped[list[dict]] = mapped_column(json_column_type(), nullable=False, default=list)
    start_location: Mapped[dict | None] = mapped_column(json_column_type(), nullable=True)
    end_location: Mapped[dict | None] = mapped_column(json_column_type(), nullable=True)
    return_leg_distance_km: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    return_leg_travel_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    explanation_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    trip_request: Mapped["TripRequest"] = relationship(back_populates="route_plans")
    recommendation_run: Mapped["RecommendationRun | None"] = relationship(back_populates="route_plans")
    feedback_entries: Mapped[list["FeedbackEntry"]] = relationship(
        back_populates="route",
        cascade="all, delete-orphan",
    )
    decision_logs: Mapped[list["DecisionLog"]] = relationship(back_populates="route")


class FeedbackEntry(Base):
    __tablename__ = "feedback_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(
        ForeignKey("route_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    trip_request_id: Mapped[int] = mapped_column(
        ForeignKey("trip_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    city_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    route_points_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_budget: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    route: Mapped["RoutePlan"] = relationship(back_populates="feedback_entries")
    trip_request: Mapped["TripRequest"] = relationship(back_populates="feedback_entries")
    decision_logs: Mapped[list["DecisionLog"]] = relationship(back_populates="feedback")


class DecisionLog(Base):
    __tablename__ = "decision_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    city_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    trip_request_id: Mapped[int | None] = mapped_column(
        ForeignKey("trip_requests.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    recommendation_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("recommendation_runs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    route_id: Mapped[int | None] = mapped_column(
        ForeignKey("route_plans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    feedback_id: Mapped[int | None] = mapped_column(
        ForeignKey("feedback_entries.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    input_context: Mapped[dict] = mapped_column(json_column_type(), nullable=False, default=dict)
    profile_snapshot: Mapped[dict | None] = mapped_column(json_column_type(), nullable=True)
    recommendations_snapshot: Mapped[list[dict] | None] = mapped_column(
        json_column_type(),
        nullable=True,
    )
    route_snapshot: Mapped[dict | None] = mapped_column(json_column_type(), nullable=True)
    explanation_snapshot: Mapped[dict | None] = mapped_column(json_column_type(), nullable=True)
    feedback_snapshot: Mapped[dict | None] = mapped_column(json_column_type(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    trip_request: Mapped["TripRequest | None"] = relationship(back_populates="decision_logs")
    recommendation_run: Mapped["RecommendationRun | None"] = relationship(back_populates="decision_logs")
    route: Mapped["RoutePlan | None"] = relationship(back_populates="decision_logs")
    feedback: Mapped["FeedbackEntry | None"] = relationship(back_populates="decision_logs")
