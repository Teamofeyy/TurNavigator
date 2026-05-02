from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

BudgetLevel = Literal["low", "medium", "high"]
Pace = Literal["relaxed", "moderate", "intensive"]
Transport = Literal["walking", "public_transport", "car", "mixed"]
ExplanationLevel = Literal["short", "detailed"]
CompromiseStrategy = Literal["balanced", "budget_first", "time_first", "experience_first"]
TrustLevel = Literal["low", "medium", "high"]
PreferredTimeWindow = Literal["morning", "afternoon", "evening"]


class UserProfileBase(BaseModel):
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
    goals: list[str] = Field(
        default_factory=list,
        description="User goals that shape the planning strategy.",
        examples=[["discover_local_food", "minimize_transfers"]],
    )
    must_have: list[str] = Field(
        default_factory=list,
        description="Trip elements the route should try to preserve.",
        examples=[["river_view", "coffee_break"]],
    )
    avoid: list[str] = Field(
        default_factory=list,
        description="Trip elements the route should avoid when possible.",
        examples=[["stairs", "crowded_malls"]],
    )
    compromise_strategy: CompromiseStrategy = Field(
        default="balanced",
        description="What to prioritize when not all preferences fit together.",
        examples=["balanced"],
    )
    trust_level: TrustLevel = Field(
        default="medium",
        description="How much autonomy the user delegates to the planner.",
        examples=["medium"],
    )
    accessibility_needs: list[str] = Field(
        default_factory=list,
        description="Accessibility or comfort requirements to preserve.",
        examples=[["wheelchair_access", "quiet_places"]],
    )
    preferred_time_windows: list[PreferredTimeWindow] = Field(
        default_factory=list,
        description="Preferred day parts for activities.",
        examples=[["morning", "evening"]],
    )


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileResponse(UserProfileBase):
    id: int = Field(description="Created profile id.", examples=[1])
    created_at: datetime = Field(description="Profile creation timestamp.")
    updated_at: datetime = Field(description="Profile update timestamp.")
