from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.city import CityResponse
from app.schemas.poi import PointOfInterestResponse
from app.services.catalog_service import get_city, list_cities, list_city_pois

router = APIRouter(tags=["cities"])


@router.get(
    "/cities",
    response_model=list[CityResponse],
    summary="List available cities",
    description=(
        "Returns cities available in the current MVP seed dataset. "
        "Each city includes the number of available points of interest."
    ),
    response_description="Available cities.",
)
async def get_cities() -> list[CityResponse]:
    return list_cities()


@router.get(
    "/cities/{city_id}",
    response_model=CityResponse,
    summary="Get city by id",
    description="Returns one city from the current MVP seed dataset.",
    response_description="City details.",
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
async def get_city_by_id(city_id: int) -> CityResponse:
    city = get_city(city_id)
    if city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found",
        )
    return city


@router.get(
    "/cities/{city_id}/pois",
    response_model=list[PointOfInterestResponse],
    summary="List city points of interest",
    description=(
        "Returns points of interest for a city. "
        "Results can be filtered by normalized category and paginated with limit/offset."
    ),
    response_description="City points of interest.",
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
async def get_city_points_of_interest(
    city_id: int,
    category: str | None = Query(
        default=None,
        description="Optional normalized category filter.",
        examples=["history"],
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=250,
        description="Maximum number of POI records to return.",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of POI records to skip.",
    ),
) -> list[PointOfInterestResponse]:
    if get_city(city_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found",
        )
    return list_city_pois(city_id=city_id, category=category, limit=limit, offset=offset)
