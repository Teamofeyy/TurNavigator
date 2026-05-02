from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from statistics import mean

from app.schemas.planning import TripRequestResponse
from app.schemas.profile import UserProfileResponse
from app.services.catalog_service import get_city, list_cities, list_city_pois
from app.services.recommender import generate_recommendations
from app.services.route_builder import build_route_plan


@dataclass(frozen=True)
class Scenario:
    city_id: int
    interests: list[str]
    budget_level: str
    max_budget: int
    pace: str
    transport: str
    goals: list[str]
    max_walking_distance_km: float = 8
    days_count: int = 2
    daily_time_limit_hours: int = 8


def build_profile(
    *,
    scenario: Scenario,
    profile_id: int,
) -> UserProfileResponse:
    now = datetime.now(UTC)
    return UserProfileResponse(
        id=profile_id,
        interests=scenario.interests,
        budget_level=scenario.budget_level,
        max_budget=scenario.max_budget,
        pace=scenario.pace,
        max_walking_distance_km=scenario.max_walking_distance_km,
        preferred_transport=scenario.transport,
        explanation_level="detailed",
        goals=scenario.goals,
        must_have=[],
        avoid=[],
        compromise_strategy="balanced",
        trust_level="medium",
        accessibility_needs=[],
        preferred_time_windows=["morning", "evening"],
        created_at=now,
        updated_at=now,
    )


def build_trip_request(
    *,
    trip_request_id: int,
    scenario: Scenario,
) -> TripRequestResponse:
    profile = build_profile(scenario=scenario, profile_id=trip_request_id)
    hotel = next(
        iter(list_city_pois(scenario.city_id, category="accommodation", limit=1)),
        None,
    )
    location = None
    if hotel is not None:
        location = {
            "address": hotel.address,
            "latitude": hotel.latitude,
            "longitude": hotel.longitude,
            "name": hotel.name,
            "poi_id": hotel.id,
        }

    return TripRequestResponse(
        id=trip_request_id,
        city_id=scenario.city_id,
        profile_id=profile.id,
        profile=profile,
        days_count=scenario.days_count,
        daily_time_limit_hours=scenario.daily_time_limit_hours,
        selected_interests=scenario.interests,
        constraints={
            "include_accommodation": False,
            "return_to_start": location is not None,
        },
        start_location=location,
        end_location=location,
        created_at=datetime.now(UTC),
    )


def precision_at_k(recommendations, k: int) -> float:
    top_items = recommendations[:k]
    if not top_items:
        return 0.0
    relevant = sum(1 for item in top_items if item.matched_interests)
    return relevant / len(top_items)


def category_coverage(city_id: int, recommendations) -> float:
    candidates = list_city_pois(city_id, limit=250)
    candidate_categories = {poi.category for poi in candidates}
    if not candidate_categories:
        return 0.0
    recommended_categories = {item.category for item in recommendations}
    return len(recommended_categories) / len(candidate_categories)


def explanation_usefulness(recommendations) -> float:
    if not recommendations:
        return 0.0
    scores: list[float] = []
    for item in recommendations:
        explanation = item.explanation.lower()
        has_interest_reference = any(interest in explanation for interest in item.matched_interests)
        has_constraint_reference = any(
            keyword in explanation
            for keyword in ("бюджет", "дистан", "темп", "огранич")
        )
        if has_interest_reference and has_constraint_reference:
            scores.append(1.0)
        elif has_interest_reference or has_constraint_reference:
            scores.append(0.5)
        else:
            scores.append(0.0)
    return mean(scores)


def context_robustness(*, scenario: Scenario, base_trip_request: TripRequestResponse, city) -> float:
    perturbed_profile = base_trip_request.profile.model_copy(
        update={
            "max_budget": int(base_trip_request.profile.max_budget * 1.2),
            "max_walking_distance_km": round(base_trip_request.profile.max_walking_distance_km + 2, 1),
        }
    )
    perturbed_trip_request = base_trip_request.model_copy(update={"profile": perturbed_profile})
    base_recommendations, _ = generate_recommendations(
        trip_request=base_trip_request,
        city=city,
        limit=6,
        include_accommodation=False,
        include_categories=None,
        exclude_categories=[],
    )
    perturbed_recommendations, _ = generate_recommendations(
        trip_request=perturbed_trip_request,
        city=city,
        limit=6,
        include_accommodation=False,
        include_categories=None,
        exclude_categories=[],
    )
    base_ids = {item.poi_id for item in base_recommendations}
    perturbed_ids = {item.poi_id for item in perturbed_recommendations}
    if not base_ids and not perturbed_ids:
        return 1.0
    return len(base_ids & perturbed_ids) / len(base_ids | perturbed_ids)


def evaluate_scenario(index: int, scenario: Scenario) -> dict[str, float | int | str]:
    city = get_city(scenario.city_id)
    if city is None:
        raise ValueError(f"City {scenario.city_id} not found")

    trip_request = build_trip_request(trip_request_id=index, scenario=scenario)
    recommendations, total_candidates = generate_recommendations(
        trip_request=trip_request,
        city=city,
        limit=6,
        include_accommodation=False,
        include_categories=None,
        exclude_categories=[],
    )
    route = build_route_plan(
        trip_request=trip_request,
        city=city,
        pois=[item.poi for item in recommendations[:5]],
        optimize_order=True,
        strict_constraints=True,
        start_location=trip_request.start_location,
        end_location=trip_request.end_location,
    )

    return {
        "city_id": scenario.city_id,
        "precision_at_5": round(precision_at_k(recommendations, 5), 3),
        "coverage": round(category_coverage(scenario.city_id, recommendations), 3),
        "budget_fit": 1.0 if route.within_budget else 0.0,
        "time_fit": 1.0 if route.within_time_limit else 0.0,
        "explanation_usefulness": round(explanation_usefulness(recommendations), 3),
        "context_robustness": round(
            context_robustness(
                scenario=scenario,
                base_trip_request=trip_request,
                city=city,
            ),
            3,
        ),
        "total_candidates": total_candidates,
        "route_points": len(route.route_points),
    }


def build_default_scenarios() -> list[Scenario]:
    available_cities = [city.id for city in list_cities()[:3]]
    scenarios: list[Scenario] = []
    for city_id in available_cities:
        scenarios.extend(
            [
                Scenario(
                    city_id=city_id,
                    interests=["history", "culture"],
                    budget_level="medium",
                    max_budget=15000,
                    pace="moderate",
                    transport="walking",
                    goals=["discover_local_culture"],
                ),
                Scenario(
                    city_id=city_id,
                    interests=["food", "nature"],
                    budget_level="low",
                    max_budget=9000,
                    pace="relaxed",
                    transport="public_transport",
                    goals=["optimize_budget"],
                ),
            ]
        )
    return scenarios


def summarize(results: list[dict[str, float | int | str]]) -> dict[str, float]:
    metric_keys = [
        "precision_at_5",
        "coverage",
        "budget_fit",
        "time_fit",
        "explanation_usefulness",
        "context_robustness",
    ]
    return {
        key: round(mean(float(result[key]) for result in results), 3)
        for key in metric_keys
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate TravelContext recommendation quality.")
    parser.add_argument("--city-id", type=int, default=None, help="Evaluate only one city id.")
    parser.add_argument("--json", action="store_true", help="Print the report as JSON.")
    args = parser.parse_args()

    scenarios = build_default_scenarios()
    if args.city_id is not None:
        scenarios = [scenario for scenario in scenarios if scenario.city_id == args.city_id]

    results = [evaluate_scenario(index, scenario) for index, scenario in enumerate(scenarios, start=1)]
    report = {
        "scenarios": results,
        "summary": summarize(results) if results else {},
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    print("TravelContext evaluation report")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print("Scenarios:")
    for item in results:
        print(json.dumps(item, ensure_ascii=False))


if __name__ == "__main__":
    main()
