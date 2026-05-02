from fastapi import APIRouter, HTTPException, status

from app.schemas.poi import PointOfInterestResponse
from app.services.catalog_service import get_poi

router = APIRouter(tags=["points-of-interest"])


@router.get(
    "/pois/{poi_id}",
    response_model=PointOfInterestResponse,
    summary="Get point of interest by id",
    description="Returns one point of interest from the current MVP seed dataset.",
    response_description="Point of interest details.",
    responses={
        404: {
            "description": "Point of interest was not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Point of interest not found"},
                },
            },
        },
    },
)
async def get_point_of_interest_by_id(poi_id: int) -> PointOfInterestResponse:
    poi = get_poi(poi_id)
    if poi is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Point of interest not found",
        )
    return poi
