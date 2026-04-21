from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API health",
    description=(
        "Returns the current backend service status. "
        "This endpoint is used for local checks, deployment checks, and screenshots."
    ),
    response_description="Backend service status.",
    responses={
        200: {
            "description": "The backend API is available.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                    },
                },
            },
        },
    },
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
