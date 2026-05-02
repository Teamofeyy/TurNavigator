from typing import Any

from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    route_id: int = Field(description="Built route id to evaluate.", examples=[1])
    rating: int = Field(
        ge=1,
        le=5,
        description="User rating of route usefulness from 1 to 5.",
        examples=[4],
    )
    comment: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional user comment about the route quality.",
        examples=["Маршрут хороший, но хотелось бы меньше музеев и больше прогулок."],
    )


class FeedbackResponse(BaseModel):
    id: int = Field(description="Saved feedback id.", examples=[1])
    route_id: int = Field(description="Route id.", examples=[1])
    trip_request_id: int = Field(description="Trip request id.", examples=[1])
    city_id: int = Field(description="City id.", examples=[6])
    rating: int = Field(ge=1, le=5, description="User rating from 1 to 5.", examples=[4])
    comment: str | None = Field(
        default=None,
        description="Optional user comment.",
        examples=["Маршрут хороший, но хотелось бы больше еды и меньше музеев."],
    )
    route_points_count: int = Field(
        ge=0,
        description="Number of points in the evaluated route.",
        examples=[5],
    )
    estimated_budget: int = Field(
        ge=0,
        description="Estimated budget of the evaluated route in rubles.",
        examples=[2950],
    )
    total_time_minutes: int = Field(
        ge=0,
        description="Total estimated route time in minutes.",
        examples=[481],
    )
    created_at: datetime = Field(description="Feedback creation timestamp.")


class DecisionLogResponse(BaseModel):
    id: int = Field(description="Decision log id.", examples=[1])
    event_type: str = Field(description="Type of planning event.", examples=["route_built"])
    city_id: int = Field(description="City id.", examples=[6])
    trip_request_id: int | None = Field(default=None, description="Related trip request id.")
    recommendation_run_id: int | None = Field(default=None, description="Related recommendation run id.")
    route_id: int | None = Field(default=None, description="Related route id.")
    feedback_id: int | None = Field(default=None, description="Related feedback id.")
    input_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Request payload and context captured for the event.",
    )
    profile_snapshot: dict[str, Any] | None = Field(
        default=None,
        description="Expanded profile snapshot used in the decision.",
    )
    recommendations_snapshot: list[dict[str, Any]] | None = Field(
        default=None,
        description="Saved recommendation list snapshot if available.",
    )
    route_snapshot: dict[str, Any] | None = Field(
        default=None,
        description="Saved route snapshot if available.",
    )
    explanation_snapshot: dict[str, Any] | None = Field(
        default=None,
        description="Explanation fragments captured for auditing.",
    )
    feedback_snapshot: dict[str, Any] | None = Field(
        default=None,
        description="Saved feedback snapshot if available.",
    )
    created_at: datetime = Field(description="Decision log creation timestamp.")
