from fastapi import APIRouter, HTTPException, status

from app.services.decision_log_store import record_decision_event
from app.schemas.planning import (
    RecommendationGenerateRequest,
    RecommendationListResponse,
    TripRequestCreate,
    TripRequestResponse,
)
from app.services.catalog_service import get_city
from app.services.planning_serialization import to_json
from app.services.recommendation_store import save_recommendation_run
from app.services.recommender import generate_recommendations
from app.services.trip_store import create_trip_request, get_trip_request

router = APIRouter(tags=["planning"])


@router.post(
    "/trip-requests",
    response_model=TripRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create trip planning request",
    description=(
        "Creates a persisted trip planning request from city, reusable user profile, "
        "trip duration, and resource constraints. The generated id can be used "
        "to request recommendations and routes."
    ),
    response_description="Created trip request.",
    responses={
        404: {
            "description": "City was not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "City not found"},
                },
            },
        },
    },
)
async def create_trip_request_endpoint(
    payload: TripRequestCreate,
) -> TripRequestResponse:
    if get_city(payload.city_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found",
        )
    try:
        trip_request = create_trip_request(payload)
    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    record_decision_event(
        event_type="trip_request_created",
        city_id=trip_request.city_id,
        trip_request_id=trip_request.id,
        input_context=to_json(payload),
        profile_snapshot=to_json(trip_request.profile),
    )
    return trip_request


@router.post(
    "/recommendations/generate",
    response_model=RecommendationListResponse,
    summary="Generate personalized recommendations",
    description=(
        "Generates a ranked list of points of interest for an existing trip request. "
        "The scoring model combines interest match, budget fit, route convenience, "
        "pace fit, popularity, and data quality, then adjusts the ranking with "
        "goals, must-have/avoid constraints, trust level, accessibility needs, "
        "and preferred time windows from the saved profile."
    ),
    response_description="Ranked recommendations with explanations.",
    responses={
        404: {
            "description": "Trip request or city was not found.",
            "content": {
                "application/json": {
                    "examples": {
                        "tripNotFound": {
                            "summary": "Trip request not found",
                            "value": {"detail": "Trip request not found"},
                        },
                        "cityNotFound": {
                            "summary": "City not found",
                            "value": {"detail": "City not found"},
                        },
                    },
                },
            },
        },
    },
)
async def generate_recommendations_endpoint(
    payload: RecommendationGenerateRequest,
) -> RecommendationListResponse:
    trip_request = get_trip_request(payload.trip_request_id)
    if trip_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip request not found",
        )

    city = get_city(trip_request.city_id)
    if city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found",
        )

    recommendations, total_candidates = generate_recommendations(
        trip_request=trip_request,
        city=city,
        limit=payload.limit,
        include_accommodation=payload.include_accommodation,
        include_categories=payload.include_categories,
        exclude_categories=payload.exclude_categories,
    )
    recommendation_run = save_recommendation_run(
        trip_request=trip_request,
        payload=payload,
        recommendations=recommendations,
        total_candidates=total_candidates,
    )
    record_decision_event(
        event_type="recommendations_generated",
        city_id=trip_request.city_id,
        trip_request_id=trip_request.id,
        recommendation_run_id=recommendation_run.recommendation_run_id,
        input_context=to_json(payload),
        profile_snapshot=to_json(trip_request.profile),
        recommendations_snapshot=to_json(recommendation_run.recommendations),
        explanation_snapshot={
            "recommendation_count": len(recommendation_run.recommendations),
        },
    )
    return recommendation_run
