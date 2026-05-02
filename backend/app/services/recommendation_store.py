from __future__ import annotations

from sqlalchemy import desc, select

from app.db.session import SessionLocal
from app.models import RecommendationRun
from app.schemas.planning import (
    RecommendationGenerateRequest,
    RecommendationListResponse,
    RecommendationResponse,
    TripRequestResponse,
)
from app.services.planning_serialization import recommendation_run_model_to_response, to_json


def save_recommendation_run(
    trip_request: TripRequestResponse,
    payload: RecommendationGenerateRequest,
    recommendations: list[RecommendationResponse],
    total_candidates: int,
) -> RecommendationListResponse:
    with SessionLocal() as session:
        recommendation_run = RecommendationRun(
            trip_request_id=trip_request.id,
            city_id=trip_request.city_id,
            request_snapshot=to_json(payload),
            recommendations=to_json(recommendations),
            total_candidates=total_candidates,
        )
        session.add(recommendation_run)
        session.commit()
        session.refresh(recommendation_run)
        return recommendation_run_model_to_response(recommendation_run)


def get_latest_recommendation_run_id(trip_request_id: int) -> int | None:
    with SessionLocal() as session:
        statement = (
            select(RecommendationRun.id)
            .where(RecommendationRun.trip_request_id == trip_request_id)
            .order_by(desc(RecommendationRun.created_at), desc(RecommendationRun.id))
            .limit(1)
        )
        return session.execute(statement).scalar_one_or_none()
