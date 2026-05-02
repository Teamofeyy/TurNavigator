from __future__ import annotations

from sqlalchemy import desc, select

from app.db.session import SessionLocal
from app.models import DecisionLog, FeedbackEntry
from app.schemas.feedback import DecisionLogResponse, FeedbackCreate, FeedbackResponse
from app.schemas.route import RoutePlanResponse
from app.services.planning_serialization import (
    decision_log_model_to_response,
    feedback_model_to_response,
    to_json,
)


def record_decision_event(
    *,
    event_type: str,
    city_id: int,
    trip_request_id: int | None = None,
    recommendation_run_id: int | None = None,
    route_id: int | None = None,
    feedback_id: int | None = None,
    input_context: dict | None = None,
    profile_snapshot: dict | None = None,
    recommendations_snapshot: list[dict] | None = None,
    route_snapshot: dict | None = None,
    explanation_snapshot: dict | None = None,
    feedback_snapshot: dict | None = None,
) -> DecisionLogResponse:
    with SessionLocal() as session:
        log_entry = DecisionLog(
            event_type=event_type,
            city_id=city_id,
            trip_request_id=trip_request_id,
            recommendation_run_id=recommendation_run_id,
            route_id=route_id,
            feedback_id=feedback_id,
            input_context=input_context or {},
            profile_snapshot=profile_snapshot,
            recommendations_snapshot=recommendations_snapshot,
            route_snapshot=route_snapshot,
            explanation_snapshot=explanation_snapshot,
            feedback_snapshot=feedback_snapshot,
        )
        session.add(log_entry)
        session.commit()
        session.refresh(log_entry)
        return decision_log_model_to_response(log_entry)


def save_feedback(
    payload: FeedbackCreate,
    route: RoutePlanResponse,
) -> FeedbackResponse:
    with SessionLocal() as session:
        feedback = FeedbackEntry(
            route_id=route.id,
            trip_request_id=route.trip_request_id,
            city_id=route.city_id,
            rating=payload.rating,
            comment=payload.comment,
            route_points_count=len(route.route_points),
            estimated_budget=route.estimated_budget,
            total_time_minutes=route.total_time_minutes,
        )
        session.add(feedback)
        session.commit()
        session.refresh(feedback)

        feedback_response = feedback_model_to_response(feedback)
        log_entry = DecisionLog(
            event_type="feedback_received",
            city_id=route.city_id,
            trip_request_id=route.trip_request_id,
            route_id=route.id,
            feedback_id=feedback.id,
            input_context=to_json(payload),
            route_snapshot=to_json(route),
            explanation_snapshot={
                "summary": route.explanation_summary,
            },
            feedback_snapshot=to_json(feedback_response),
        )
        session.add(log_entry)
        session.commit()
        return feedback_response


def list_decision_logs(limit: int = 20) -> list[DecisionLogResponse]:
    with SessionLocal() as session:
        statement = (
            select(DecisionLog)
            .order_by(desc(DecisionLog.created_at), desc(DecisionLog.id))
            .limit(limit)
        )
        logs = session.scalars(statement).all()
        return [decision_log_model_to_response(log_entry) for log_entry in logs]
