from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi.encoders import jsonable_encoder

from app.models.planning import (
    DecisionLog,
    FeedbackEntry,
    RecommendationRun,
    RoutePlan,
    TripRequest,
    UserProfile,
)
from app.schemas.feedback import DecisionLogResponse, FeedbackResponse
from app.schemas.planning import (
    RecommendationListResponse,
    RecommendationResponse,
    TripLocationResponse,
    TripRequestResponse,
)
from app.schemas.profile import UserProfileCreate, UserProfileResponse
from app.schemas.route import RoutePlanResponse, RoutePointResponse


def to_json(value: Any) -> Any:
    return jsonable_encoder(value)


def profile_model_to_response(profile: UserProfile) -> UserProfileResponse:
    return UserProfileResponse(
        id=profile.id,
        profile_name=profile.profile_name,
        interests=list(profile.interests),
        budget_level=profile.budget_level,
        max_budget=profile.max_budget,
        pace=profile.pace,
        max_walking_distance_km=profile.max_walking_distance_km,
        preferred_transport=profile.preferred_transport,
        explanation_level=profile.explanation_level,
        goals=list(profile.goals),
        must_have=list(profile.must_have),
        avoid=list(profile.avoid),
        compromise_strategy=profile.compromise_strategy,
        trust_level=profile.trust_level,
        accessibility_needs=list(profile.accessibility_needs),
        preferred_time_windows=list(profile.preferred_time_windows),
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


def profile_payload_to_snapshot(
    payload: UserProfileCreate,
    *,
    profile_id: int,
    created_at: datetime,
    updated_at: datetime,
) -> dict[str, Any]:
    return to_json(
        UserProfileResponse(
            id=profile_id,
            created_at=created_at,
            updated_at=updated_at,
            **payload.model_dump(),
        )
    )


def trip_request_model_to_response(trip_request: TripRequest) -> TripRequestResponse:
    profile = _profile_response_from_trip_request(trip_request)
    return TripRequestResponse(
        id=trip_request.id,
        city_id=trip_request.city_id,
        profile_id=trip_request.profile_id,
        profile=profile,
        days_count=trip_request.days_count,
        daily_time_limit_hours=trip_request.daily_time_limit_hours,
        selected_interests=list(trip_request.selected_interests),
        constraints=dict(trip_request.constraints),
        start_location=_trip_location_response(trip_request.start_location),
        end_location=_trip_location_response(trip_request.end_location),
        created_at=trip_request.created_at,
    )


def recommendation_run_model_to_response(
    recommendation_run: RecommendationRun,
) -> RecommendationListResponse:
    return RecommendationListResponse(
        recommendation_run_id=recommendation_run.id,
        trip_request_id=recommendation_run.trip_request_id,
        city_id=recommendation_run.city_id,
        total_candidates=recommendation_run.total_candidates,
        recommendations=[
            RecommendationResponse.model_validate(item)
            for item in recommendation_run.recommendations
        ],
    )


def route_plan_model_to_response(route_plan: RoutePlan) -> RoutePlanResponse:
    return RoutePlanResponse(
        id=route_plan.id,
        trip_request_id=route_plan.trip_request_id,
        city_id=route_plan.city_id,
        status=route_plan.status,
        total_distance_km=route_plan.total_distance_km,
        total_travel_minutes=route_plan.total_travel_minutes,
        total_visit_minutes=route_plan.total_visit_minutes,
        total_time_minutes=route_plan.total_time_minutes,
        estimated_budget=route_plan.estimated_budget,
        days_count=route_plan.days_count,
        daily_time_limit_minutes=route_plan.daily_time_limit_minutes,
        within_time_limit=route_plan.within_time_limit,
        within_budget=route_plan.within_budget,
        start_location=_trip_location_response(route_plan.start_location),
        end_location=_trip_location_response(route_plan.end_location),
        return_leg_distance_km=route_plan.return_leg_distance_km,
        return_leg_travel_minutes=route_plan.return_leg_travel_minutes,
        skipped_poi_ids=list(route_plan.skipped_poi_ids),
        route_points=[
            RoutePointResponse.model_validate(point)
            for point in route_plan.route_points
        ],
        explanation_summary=route_plan.explanation_summary,
    )


def feedback_model_to_response(feedback: FeedbackEntry) -> FeedbackResponse:
    return FeedbackResponse(
        id=feedback.id,
        route_id=feedback.route_id,
        trip_request_id=feedback.trip_request_id,
        city_id=feedback.city_id,
        rating=feedback.rating,
        comment=feedback.comment,
        route_points_count=feedback.route_points_count,
        estimated_budget=feedback.estimated_budget,
        total_time_minutes=feedback.total_time_minutes,
        created_at=feedback.created_at,
    )


def decision_log_model_to_response(log_entry: DecisionLog) -> DecisionLogResponse:
    return DecisionLogResponse(
        id=log_entry.id,
        event_type=log_entry.event_type,
        city_id=log_entry.city_id,
        trip_request_id=log_entry.trip_request_id,
        recommendation_run_id=log_entry.recommendation_run_id,
        route_id=log_entry.route_id,
        feedback_id=log_entry.feedback_id,
        input_context=log_entry.input_context or {},
        profile_snapshot=log_entry.profile_snapshot,
        recommendations_snapshot=log_entry.recommendations_snapshot,
        route_snapshot=log_entry.route_snapshot,
        explanation_snapshot=log_entry.explanation_snapshot,
        feedback_snapshot=log_entry.feedback_snapshot,
        created_at=log_entry.created_at,
    )


def _profile_response_from_trip_request(trip_request: TripRequest) -> UserProfileResponse:
    if trip_request.profile is not None:
        return profile_model_to_response(trip_request.profile)
    return UserProfileResponse.model_validate(trip_request.profile_snapshot)


def _trip_location_response(data: dict[str, Any] | None) -> TripLocationResponse | None:
    if data is None:
        return None
    return TripLocationResponse.model_validate(data)
