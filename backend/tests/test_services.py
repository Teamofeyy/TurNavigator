from __future__ import annotations

from datetime import UTC, datetime

from app.schemas.planning import TripLocationResponse, TripRequestResponse
from app.schemas.profile import UserProfileResponse
from app.services.catalog_service import get_city, list_city_pois
from app.services.recommender import generate_recommendations
from app.services.route_builder import build_route_plan


def test_recommender_returns_interest_matched_items():
    city = get_city(6)
    assert city is not None

    profile = UserProfileResponse(
        id=1,
        interests=["food", "culture"],
        budget_level="medium",
        max_budget=15000,
        pace="moderate",
        max_walking_distance_km=8,
        preferred_transport="walking",
        explanation_level="detailed",
        goals=["discover_local_culture"],
        must_have=["coffee_break"],
        avoid=[],
        compromise_strategy="balanced",
        trust_level="medium",
        accessibility_needs=[],
        preferred_time_windows=["morning"],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    trip_request = TripRequestResponse(
        id=1,
        city_id=city.id,
        profile_id=profile.id,
        profile=profile,
        days_count=2,
        daily_time_limit_hours=8,
        selected_interests=["food", "culture"],
        constraints={"include_accommodation": False},
        start_location=None,
        end_location=None,
        created_at=datetime.now(UTC),
    )

    recommendations, total_candidates = generate_recommendations(
        trip_request=trip_request,
        city=city,
        limit=5,
        include_accommodation=False,
        include_categories=None,
        exclude_categories=[],
    )

    assert total_candidates >= len(recommendations)
    assert recommendations
    assert all(item.score >= 0 for item in recommendations)
    assert all(item.matched_interests for item in recommendations[:3])


def test_route_builder_starts_and_returns_to_hotel():
    city = get_city(6)
    assert city is not None

    pois = list_city_pois(city.id, limit=40)
    hotel = next(poi for poi in pois if poi.category == "accommodation")
    route_candidates = [poi for poi in pois if poi.category != "accommodation"][:4]
    assert route_candidates

    profile = UserProfileResponse(
        id=1,
        interests=["history", "food"],
        budget_level="medium",
        max_budget=20000,
        pace="moderate",
        max_walking_distance_km=10,
        preferred_transport="walking",
        explanation_level="detailed",
        goals=["maximize_variety"],
        must_have=[],
        avoid=[],
        compromise_strategy="balanced",
        trust_level="medium",
        accessibility_needs=[],
        preferred_time_windows=["morning", "evening"],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    trip_request = TripRequestResponse(
        id=1,
        city_id=city.id,
        profile_id=profile.id,
        profile=profile,
        days_count=2,
        daily_time_limit_hours=8,
        selected_interests=["history", "food"],
        constraints={"return_to_start": True},
        start_location=TripLocationResponse.model_validate(
            {
                "address": hotel.address,
                "latitude": hotel.latitude,
                "longitude": hotel.longitude,
                "name": hotel.name,
                "poi_id": hotel.id,
            }
        ),
        end_location=TripLocationResponse.model_validate(
            {
                "address": hotel.address,
                "latitude": hotel.latitude,
                "longitude": hotel.longitude,
                "name": hotel.name,
                "poi_id": hotel.id,
            }
        ),
        created_at=datetime.now(UTC),
    )

    route = build_route_plan(
        trip_request=trip_request,
        city=city,
        pois=route_candidates,
        optimize_order=True,
        strict_constraints=True,
        start_location=trip_request.start_location,
        end_location=trip_request.end_location,
    )

    assert route.start_location is not None
    assert route.end_location is not None
    assert route.start_location.poi_id == hotel.id
    assert route.end_location.poi_id == hotel.id
    assert route.route_points
    assert route.route_points[0].leg_distance_km >= 0
    assert route.return_leg_distance_km >= 0
    assert "старт" in route.explanation_summary.lower()
