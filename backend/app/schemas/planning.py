from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.schemas.poi import PointOfInterestResponse
from app.schemas.profile import UserProfileCreate, UserProfileResponse


class TripLocationInput(BaseModel):
    address: str = Field(description="Human-readable location address.", examples=["ул. Большая Садовая, 121"])
    latitude: float = Field(description="Location latitude.", examples=[47.2269])
    longitude: float = Field(description="Location longitude.", examples=[39.7139])
    name: str | None = Field(default=None, description="Optional location label.", examples=["Отель"])
    poi_id: int | None = Field(default=None, description="Optional accommodation POI id.", examples=[6012])


class TripLocationResponse(TripLocationInput):
    pass


class TripRequestCreate(BaseModel):
    city_id: int = Field(description="City id for trip planning.", examples=[6])
    profile_id: int | None = Field(
        default=None,
        description="Existing saved profile id to reuse for this trip.",
        examples=[1],
    )
    profile: UserProfileCreate | None = Field(
        default=None,
        description="Inline profile to persist and attach to the trip request.",
    )
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
    start_location: TripLocationInput | None = Field(
        default=None,
        description="Preferred start point such as a selected hotel.",
    )
    end_location: TripLocationInput | None = Field(
        default=None,
        description="Preferred end point. If omitted, the route may return to the start location.",
    )

    @model_validator(mode="after")
    def validate_profile_source(self) -> "TripRequestCreate":
        has_profile = self.profile is not None
        has_profile_id = self.profile_id is not None
        if has_profile == has_profile_id:
            raise ValueError("Provide exactly one of profile or profile_id.")
        return self


class TripRequestResponse(BaseModel):
    id: int = Field(description="Created trip request id.", examples=[1])
    city_id: int = Field(description="City id for trip planning.", examples=[6])
    profile_id: int = Field(description="Persisted user profile id.", examples=[1])
    profile: UserProfileResponse
    days_count: int = Field(description="Trip duration in days.", examples=[2])
    daily_time_limit_hours: int = Field(description="Available planning time per day.", examples=[8])
    selected_interests: list[str] | None = Field(
        default=None,
        description="Interests selected for this trip.",
    )
    constraints: dict[str, str | int | float | bool] = Field(
        default_factory=dict,
        description="Trip-level constraints snapshot.",
    )
    start_location: TripLocationResponse | None = Field(default=None, description="Trip start point.")
    end_location: TripLocationResponse | None = Field(default=None, description="Trip end point.")
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
    recommendation_run_id: int = Field(description="Persisted recommendation run id.", examples=[1])
    trip_request_id: int = Field(description="Trip request id.", examples=[1])
    city_id: int = Field(description="City id.", examples=[6])
    total_candidates: int = Field(description="Number of candidate POIs before limiting.", examples=[7])
    recommendations: list[RecommendationResponse]
