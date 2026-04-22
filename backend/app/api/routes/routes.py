from fastapi import APIRouter, HTTPException, status

from app.schemas.poi import PointOfInterestResponse
from app.schemas.route import RouteBuildRequest, RoutePlanResponse
from app.services.recommender import generate_recommendations
from app.services.route_builder import build_route_plan
from app.services.route_store import get_route, save_route
from app.services.seed_loader import get_city, get_poi
from app.services.trip_store import get_trip_request

router = APIRouter(tags=["routes"])


@router.post(
    "/routes/build",
    response_model=RoutePlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Build route plan",
    description=(
        "Builds an ordered route from selected POIs or from generated recommendations. "
        "The route builder estimates distance, movement time, visit time, budget, "
        "and checks whether the plan fits time and budget constraints."
    ),
    response_description="Built route plan.",
    responses={
        400: {
            "description": "Invalid route candidate.",
            "content": {
                "application/json": {
                    "example": {"detail": "POI 1001 does not belong to trip city"},
                },
            },
        },
        404: {
            "description": "Trip request or POI was not found.",
            "content": {
                "application/json": {
                    "examples": {
                        "tripNotFound": {
                            "summary": "Trip request not found",
                            "value": {"detail": "Trip request not found"},
                        },
                        "poiNotFound": {
                            "summary": "POI not found",
                            "value": {"detail": "POI not found"},
                        },
                    },
                },
            },
        },
    },
)
async def build_route_endpoint(payload: RouteBuildRequest) -> RoutePlanResponse:
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

    pois = _resolve_route_pois(payload=payload, city_id=trip_request.city_id)
    route_plan = build_route_plan(
        trip_request=trip_request,
        city=city,
        pois=pois,
        optimize_order=payload.optimize_order,
        strict_constraints=payload.strict_constraints,
    )
    return save_route(route_plan)


@router.get(
    "/routes/{route_id}",
    response_model=RoutePlanResponse,
    summary="Get route plan by id",
    description="Returns a previously built in-memory route plan.",
    response_description="Route plan details.",
    responses={
        404: {
            "description": "Route plan was not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Route not found"},
                },
            },
        },
    },
)
async def get_route_endpoint(route_id: int) -> RoutePlanResponse:
    route = get_route(route_id)
    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )
    return route


def _resolve_route_pois(
    payload: RouteBuildRequest,
    city_id: int,
) -> list[PointOfInterestResponse]:
    if payload.poi_ids:
        return _resolve_explicit_pois(
            poi_ids=payload.poi_ids[: payload.max_points],
            city_id=city_id,
        )

    trip_request = get_trip_request(payload.trip_request_id)
    if trip_request is None:
        return []
    city = get_city(city_id)
    if city is None:
        return []

    recommendations, _ = generate_recommendations(
        trip_request=trip_request,
        city=city,
        limit=payload.max_points,
        include_accommodation=False,
        include_categories=None,
        exclude_categories=[],
    )
    return [recommendation.poi for recommendation in recommendations]


def _resolve_explicit_pois(
    poi_ids: list[int],
    city_id: int,
) -> list[PointOfInterestResponse]:
    pois: list[PointOfInterestResponse] = []
    for poi_id in poi_ids:
        poi = get_poi(poi_id)
        if poi is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="POI not found",
            )
        if poi.city_id != city_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"POI {poi_id} does not belong to trip city",
            )
        pois.append(poi)
    return pois
