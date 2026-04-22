from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.poi import PointOfInterestResponse

BudgetLevel = Literal["low", "medium", "high"]
Pace = Literal["relaxed", "moderate", "intensive"]
Transport = Literal["walking", "public_transport", "car", "mixed"]
ExplanationLevel = Literal["short", "detailed"]


class UserProfileInput(BaseModel):
    interests: list[str] = Field(
        min_length=1,
        description="User interests used for personalization.",
        examples=[["culture", "food", "history"]],
    )
    budget_level: BudgetLevel = Field(
        default="medium",
        description="Qualitative user budget level.",
        examples=["medium"],
    )
    max_budget: int = Field(
        ge=0,
        description="Maximum available trip budget in Russian rubles.",
        examples=[15000],
    )
    pace: Pace = Field(
        default="moderate",
        description="Preferred trip pace.",
        examples=["moderate"],
    )
    max_walking_distance_km: float = Field(
        default=8,
        ge=0,
        description="Maximum preferred walking distance per day.",
        examples=[8],
    )
    preferred_transport: Transport = Field(
        default="walking",
        description="Preferred transport mode.",
        examples=["walking"],
    )
    explanation_level: ExplanationLevel = Field(
        default="detailed",
        description="Preferred level of recommendation explanation.",
        examples=["detailed"],
    )


class TripRequestCreate(BaseModel):
    city_id: int = Field(description="City id for trip planning.", examples=[6])
    profile: UserProfileInput
    days_count: int = Field(
        default=1,
        ge=1,
        le=14,
        description="Trip duration in days.",
        examples=[1],
    )
    daily_time_limit_hours: int = Field(
        default=8,
        ge=1,
        le=16,
        description="Available planning time per day.",
        examples=[8],
    )
    selected_interests: list[str] | None = Field(
        default=None,
        description="Optional interests selected for this specific trip. If omitted, profile interests are used.",
        examples=[["food", "history", "walking"]],
    )
    constraints: dict[str, str | int | float | bool] = Field(
        default_factory=dict,
        description="Additional planning constraints for future extensions.",
        examples=[{"avoid_expensive": True}],
    )


class TripRequestResponse(TripRequestCreate):
    id: int = Field(description="Created trip request id.", examples=[1])
    created_at: datetime = Field(description="Creation timestamp.")


class RecommendationGenerateRequest(BaseModel):
    trip_request_id: int = Field(
        description="Previously created trip request id.",
        examples=[1],
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of recommendations to return.",
        examples=[8],
    )
    include_accommodation: bool = Field(
        default=False,
        description="Whether accommodation objects should be included in recommendations.",
        examples=[False],
    )
    include_categories: list[str] | None = Field(
        default=None,
        description="Optional category allow-list.",
        examples=[["history", "culture", "food", "nature"]],
    )
    exclude_categories: list[str] = Field(
        default_factory=list,
        description="Optional category deny-list.",
        examples=[["shopping"]],
    )


class RecommendationFactors(BaseModel):
    interest_match: float = Field(ge=0, le=1, description="Interest match factor.")
    budget_match: float = Field(ge=0, le=1, description="Budget fit factor.")
    route_convenience: float = Field(ge=0, le=1, description="Distance and route convenience factor.")
    pace_match: float = Field(ge=0, le=1, description="Pace fit factor.")
    popularity_score: float = Field(ge=0, le=1, description="POI popularity factor.")
    data_quality_score: float = Field(ge=0, le=1, description="POI data quality factor.")


class ConstraintStatus(BaseModel):
    budget: str = Field(description="Budget constraint status.", examples=["within_budget"])
    pace: str = Field(description="Pace constraint status.", examples=["fits_moderate_pace"])
    distance: str = Field(description="Distance constraint status.", examples=["near_city_center"])


class RecommendationResponse(BaseModel):
    poi_id: int = Field(description="Recommended POI id.", examples=[6005])
    name: str = Field(description="Recommended POI name.", examples=["Золотой колос"])
    category: str = Field(description="Recommended POI category.", examples=["food"])
    score: float = Field(ge=0, le=1, description="Final normalized recommendation score.", examples=[0.86])
    rank: int = Field(ge=1, description="Recommendation rank.", examples=[1])
    matched_interests: list[str] = Field(
        description="User interests matched by this POI.",
        examples=[["food", "coffee"]],
    )
    factors: RecommendationFactors
    constraint_status: ConstraintStatus
    explanation: str = Field(description="Human-readable recommendation explanation.")
    poi: PointOfInterestResponse


class RecommendationListResponse(BaseModel):
    trip_request_id: int = Field(description="Trip request id.", examples=[1])
    city_id: int = Field(description="City id.", examples=[6])
    total_candidates: int = Field(description="Number of candidate POIs before limiting.", examples=[7])
    recommendations: list[RecommendationResponse]
