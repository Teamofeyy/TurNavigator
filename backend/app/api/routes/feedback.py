from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.feedback import DecisionLogResponse, FeedbackCreate, FeedbackResponse
from app.services.decision_log_store import list_decision_logs, save_feedback
from app.services.route_store import get_route

router = APIRouter(tags=["feedback"])


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save route feedback",
    description=(
        "Stores a user evaluation for a previously built route. The feedback entry "
        "is also written into the in-memory decision log for MVP experiments."
    ),
    response_description="Saved feedback entry.",
    responses={
        404: {
            "description": "Route was not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Route not found"},
                },
            },
        },
    },
)
async def create_feedback_endpoint(payload: FeedbackCreate) -> FeedbackResponse:
    route = get_route(payload.route_id)
    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )
    return save_feedback(payload=payload, route=route)


@router.get(
    "/decision-logs",
    response_model=list[DecisionLogResponse],
    summary="List decision log entries",
    description=(
        "Returns recent feedback and decision log entries created during the MVP "
        "session. This is useful for experiments and demonstration of explainable "
        "planning history."
    ),
    response_description="Recent decision log entries.",
)
async def list_decision_logs_endpoint(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of log entries to return.",
    ),
) -> list[DecisionLogResponse]:
    return list_decision_logs(limit=limit)
