from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.poi import PointOfInterestResponse

RouteStatus = Literal["built", "partially_built", "empty"]


class RouteBuildRequest(BaseModel):
    trip_request_id: int = Field(
        description="Existing trip request id.",
        examples=[1],
    )
    poi_ids: list[int] | None = Field(
        default=None,
        description=(
            "Optional explicit POI ids to include. If omitted, the backend uses "
            "the recommendation engine to select route candidates."
        ),
        examples=[[6005, 6002, 6004, 6001]],
    )
    max_points: int = Field(
        default=6,
        ge=1,
        le=20,
        description="Maximum number of POIs to include in the route.",
        examples=[5],
    )
    optimize_order: bool = Field(
        default=True,
        description="Whether to order POIs with a nearest-neighbor heuristic.",
        examples=[True],
    )
    strict_constraints: bool = Field(
        default=True,
        description="Skip POIs that would exceed time or budget constraints when possible.",
        examples=[True],
    )


class RoutePointResponse(BaseModel):
    order: int = Field(ge=1, description="Point order in the route.", examples=[1])
    poi_id: int = Field(description="POI id.", examples=[6005])
    name: str = Field(description="POI name.", examples=["Золотой колос"])
    category: str = Field(description="POI category.", examples=["food"])
    latitude: float = Field(description="POI latitude.", examples=[47.220524])
    longitude: float = Field(description="POI longitude.", examples=[39.708275])
    leg_distance_km: float = Field(
        ge=0,
        description="Distance from previous route point or city center.",
        examples=[1.8],
    )
    leg_travel_minutes: int = Field(
        ge=0,
        description="Estimated travel time from previous route point.",
        examples=[24],
    )
    visit_minutes: int = Field(
        ge=0,
        description="Estimated visit duration.",
        examples=[50],
    )
    estimated_cost_rub: int = Field(
        ge=0,
        description="Estimated cost for this point.",
        examples=[500],
    )
    cumulative_distance_km: float = Field(
        ge=0,
        description="Route distance accumulated up to this point.",
        examples=[1.8],
    )
    cumulative_time_minutes: int = Field(
        ge=0,
        description="Travel plus visit time accumulated up to this point.",
        examples=[74],
    )
    cumulative_budget_rub: int = Field(
        ge=0,
        description="Budget accumulated up to this point.",
        examples=[500],
    )
    poi: PointOfInterestResponse


class RoutePlanResponse(BaseModel):
    id: int = Field(description="Route plan id.", examples=[1])
    trip_request_id: int = Field(description="Trip request id.", examples=[1])
    city_id: int = Field(description="City id.", examples=[6])
    status: RouteStatus = Field(description="Route build status.", examples=["built"])
    total_distance_km: float = Field(
        ge=0,
        description="Total route distance in kilometers.",
        examples=[5.4],
    )
    total_travel_minutes: int = Field(
        ge=0,
        description="Total estimated movement time.",
        examples=[72],
    )
    total_visit_minutes: int = Field(
        ge=0,
        description="Total estimated POI visit time.",
        examples=[250],
    )
    total_time_minutes: int = Field(
        ge=0,
        description="Total movement plus visit time.",
        examples=[322],
    )
    estimated_budget: int = Field(
        ge=0,
        description="Total estimated route budget in Russian rubles.",
        examples=[850],
    )
    days_count: int = Field(ge=1, description="Trip duration in days.", examples=[1])
    daily_time_limit_minutes: int = Field(
        ge=1,
        description="Available planning time per day in minutes.",
        examples=[480],
    )
    within_time_limit: bool = Field(
        description="Whether the route fits the total time limit.",
        examples=[True],
    )
    within_budget: bool = Field(
        description="Whether the route fits the profile budget.",
        examples=[True],
    )
    skipped_poi_ids: list[int] = Field(
        description="POI ids skipped because of route constraints.",
        examples=[[6008]],
    )
    route_points: list[RoutePointResponse]
    explanation_summary: str = Field(description="Human-readable route explanation.")
