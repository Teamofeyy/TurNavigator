from fastapi import APIRouter, HTTPException, status

from app.schemas.planning import (
    RecommendationGenerateRequest,
    RecommendationListResponse,
    TripRequestCreate,
    TripRequestResponse,
)
from app.services.catalog_service import get_city
from app.services.recommender import generate_recommendations
from app.services.trip_store import create_trip_request, get_trip_request

router = APIRouter(tags=["planning"])


@router.post(
    "/trip-requests",
    response_model=TripRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create trip planning request",
    description=(
        "Creates an in-memory trip planning request from city, user profile, "
        "trip duration, and resource constraints. The generated id can be used "
        "to request recommendations."
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
    return create_trip_request(payload)


@router.post(
    "/recommendations/generate",
    response_model=RecommendationListResponse,
    summary="Generate personalized recommendations",
    description=(
        "Generates a ranked list of points of interest for an existing trip request. "
        "The scoring model combines interest match, budget fit, route convenience, "
        "pace fit, popularity, and data quality."
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
    return RecommendationListResponse(
        trip_request_id=trip_request.id,
        city_id=trip_request.city_id,
        total_candidates=total_candidates,
        recommendations=recommendations,
    )
