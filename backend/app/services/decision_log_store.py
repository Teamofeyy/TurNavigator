from datetime import UTC, datetime
from itertools import count

from app.schemas.feedback import DecisionLogResponse, FeedbackCreate, FeedbackResponse
from app.schemas.route import RoutePlanResponse

_decision_log_id_sequence = count(1)
_decision_logs: dict[int, DecisionLogResponse] = {}


def save_feedback(
    payload: FeedbackCreate,
    route: RoutePlanResponse,
) -> FeedbackResponse:
    feedback_id = next(_decision_log_id_sequence)
    log_entry = DecisionLogResponse(
        id=feedback_id,
        route_id=route.id,
        trip_request_id=route.trip_request_id,
        city_id=route.city_id,
        rating=payload.rating,
        comment=payload.comment,
        route_points_count=len(route.route_points),
        estimated_budget=route.estimated_budget,
        total_time_minutes=route.total_time_minutes,
        created_at=datetime.now(UTC),
    )
    _decision_logs[feedback_id] = log_entry
    return FeedbackResponse(**log_entry.model_dump())


def list_decision_logs(limit: int = 20) -> list[DecisionLogResponse]:
    logs = sorted(
        _decision_logs.values(),
        key=lambda item: item.created_at,
        reverse=True,
    )
    return logs[:limit]
