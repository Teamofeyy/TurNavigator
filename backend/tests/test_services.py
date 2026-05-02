from __future__ import annotations

from datetime import UTC, datetime

import app.services.recommender as recommender_service
from app.schemas.city import CityResponse
from app.schemas.planning import TripLocationResponse, TripRequestResponse
from app.schemas.poi import PointOfInterestResponse
from app.schemas.profile import UserProfileResponse
from app.services.recommender import generate_recommendations
from app.services.route_builder import build_route_plan


def test_recommender_uses_profile_signals_in_scoring_and_explanation(monkeypatch):
    city = _build_city()
    quiet_cafe = _build_poi(
        poi_id=1,
        name="Riverside Breakfast Cafe",
        category="food",
        subcategory="cafe",
        latitude=47.23,
        longitude=39.72,
        description="Quiet accessible cafe with river view and local breakfast.",
        average_cost_rub=900,
        estimated_visit_minutes=60,
        popularity_score=0.75,
        data_quality_score=0.82,
        interests=["food", "culture"],
        osm_tags={"wheelchair": "yes", "viewpoint": "river"},
    )
    loud_bar = _build_poi(
        poi_id=2,
        name="Central Stairs Bar",
        category="food",
        subcategory="bar",
        latitude=47.235,
        longitude=39.721,
        description="Crowded bar with stairs and loud music.",
        average_cost_rub=1100,
        estimated_visit_minutes=75,
        popularity_score=0.78,
        data_quality_score=0.8,
        interests=["food", "nightlife"],
        osm_tags={"access": "stairs_only"},
    )
    city_museum = _build_poi(
        poi_id=3,
        name="City History Museum",
        category="culture",
        subcategory="museum",
        latitude=47.229,
        longitude=39.719,
        description="Local history museum with quiet halls and photo gallery.",
        average_cost_rub=700,
        estimated_visit_minutes=80,
        popularity_score=0.74,
        data_quality_score=0.9,
        interests=["culture", "history", "architecture"],
        osm_tags={"tourism": "museum"},
    )
    monkeypatch.setattr(
        recommender_service,
        "list_city_pois",
        lambda city_id, limit, offset: [quiet_cafe, loud_bar, city_museum],
    )

    trip_request = _build_trip_request(
        profile=_build_profile(
            interests=["food"],
            goals=["discover_local_culture"],
            must_have=["river view"],
            avoid=["stairs"],
            compromise_strategy="balanced",
            trust_level="medium",
            accessibility_needs=["wheelchair_access", "quiet_places"],
            preferred_time_windows=["morning"],
        )
    )

    recommendations, total_candidates = generate_recommendations(
        trip_request=trip_request,
        city=city,
        limit=3,
        include_accommodation=False,
        include_categories=None,
        exclude_categories=[],
    )

    assert total_candidates == 3
    assert [item.poi_id for item in recommendations] == [1, 3, 2]
    assert recommendations[0].score > recommendations[-1].score
    assert "must-have" in recommendations[0].explanation.lower()
    assert "accessibility needs" in recommendations[0].explanation.lower()
    assert "цели поездки" in recommendations[1].explanation.lower()


def test_recommender_changes_ranking_for_strategy_and_trust(monkeypatch):
    city = _build_city()
    classic_cafe = _build_poi(
        poi_id=11,
        name="Classic Cafe",
        category="food",
        subcategory="cafe",
        latitude=47.23,
        longitude=39.72,
        description="Reliable city cafe close to the hotel.",
        average_cost_rub=600,
        estimated_visit_minutes=55,
        popularity_score=0.55,
        data_quality_score=0.7,
        interests=["food"],
        osm_tags={"amenity": "cafe"},
    )
    skyline_view = _build_poi(
        poi_id=12,
        name="Skyline Observation Deck",
        category="architecture",
        subcategory="lookout",
        latitude=47.235,
        longitude=39.725,
        description="Panoramic photo spot with city view.",
        average_cost_rub=1800,
        estimated_visit_minutes=95,
        popularity_score=0.95,
        data_quality_score=0.95,
        interests=["architecture", "culture"],
        osm_tags={"tourism": "viewpoint"},
    )
    monkeypatch.setattr(
        recommender_service,
        "list_city_pois",
        lambda city_id, limit, offset: [classic_cafe, skyline_view],
    )

    conservative_request = _build_trip_request(
        profile=_build_profile(
            interests=["food"],
            goals=["photo_spots"],
            compromise_strategy="budget_first",
            trust_level="low",
        )
    )
    exploratory_request = _build_trip_request(
        profile=_build_profile(
            interests=["food"],
            goals=["photo_spots"],
            compromise_strategy="experience_first",
            trust_level="high",
        )
    )

    conservative_recommendations, _ = generate_recommendations(
        trip_request=conservative_request,
        city=city,
        limit=2,
        include_accommodation=False,
        include_categories=None,
        exclude_categories=[],
    )
    exploratory_recommendations, _ = generate_recommendations(
        trip_request=exploratory_request,
        city=city,
        limit=2,
        include_accommodation=False,
        include_categories=None,
        exclude_categories=[],
    )

    assert conservative_recommendations[0].poi_id == classic_cafe.id
    assert exploratory_recommendations[0].poi_id == skyline_view.id


def test_route_builder_strict_constraints_keep_time_for_return_to_hotel():
    city = _build_city()
    hotel_location = TripLocationResponse.model_validate(
        {
            "address": "Hotel quay 1",
            "latitude": 47.22,
            "longitude": 39.71,
            "name": "Hotel",
            "poi_id": 900,
        }
    )
    far_poi = _build_poi(
        poi_id=21,
        name="Far Riverside Park",
        category="nature",
        subcategory="park",
        latitude=47.26,
        longitude=39.71,
        description="Large riverside park.",
        average_cost_rub=0,
        estimated_visit_minutes=20,
        popularity_score=0.8,
        data_quality_score=0.8,
        interests=["nature"],
        osm_tags={"leisure": "park"},
    )
    trip_request = _build_trip_request(
        profile=_build_profile(
            interests=["nature"],
            goals=[],
            max_budget=10000,
            preferred_transport="walking",
        ),
        days_count=1,
        daily_time_limit_hours=2,
        start_location=hotel_location,
        end_location=hotel_location,
    )

    strict_route = build_route_plan(
        trip_request=trip_request,
        city=city,
        pois=[far_poi],
        optimize_order=True,
        strict_constraints=True,
        start_location=hotel_location,
        end_location=hotel_location,
    )
    relaxed_route = build_route_plan(
        trip_request=trip_request,
        city=city,
        pois=[far_poi],
        optimize_order=True,
        strict_constraints=False,
        start_location=hotel_location,
        end_location=hotel_location,
    )

    assert strict_route.route_points == []
    assert strict_route.skipped_poi_ids == [far_poi.id]
    assert relaxed_route.route_points
    assert relaxed_route.return_leg_travel_minutes > 0


def _build_city() -> CityResponse:
    return CityResponse(
        id=77,
        name="Test City",
        region="Region",
        country="Russia",
        latitude=47.22,
        longitude=39.71,
        population=1_000_000,
        source="test",
        external_id="test-city",
        wikidata_id=None,
        osm_id=None,
        pois_count=12,
    )


def _build_profile(
    *,
    interests: list[str],
    goals: list[str],
    must_have: list[str] | None = None,
    avoid: list[str] | None = None,
    compromise_strategy: str = "balanced",
    trust_level: str = "medium",
    accessibility_needs: list[str] | None = None,
    preferred_time_windows: list[str] | None = None,
    max_budget: int = 12000,
    preferred_transport: str = "walking",
) -> UserProfileResponse:
    now = datetime.now(UTC)
    return UserProfileResponse(
        id=1,
        profile_name="Test profile",
        interests=interests,
        budget_level="medium",
        max_budget=max_budget,
        pace="moderate",
        max_walking_distance_km=8,
        preferred_transport=preferred_transport,
        explanation_level="detailed",
        goals=goals,
        must_have=must_have or [],
        avoid=avoid or [],
        compromise_strategy=compromise_strategy,  # type: ignore[arg-type]
        trust_level=trust_level,  # type: ignore[arg-type]
        accessibility_needs=accessibility_needs or [],
        preferred_time_windows=preferred_time_windows or [],
        created_at=now,
        updated_at=now,
    )


def _build_trip_request(
    *,
    profile: UserProfileResponse,
    days_count: int = 2,
    daily_time_limit_hours: int = 8,
    start_location: TripLocationResponse | None = None,
    end_location: TripLocationResponse | None = None,
) -> TripRequestResponse:
    return TripRequestResponse(
        id=1,
        city_id=77,
        profile_id=profile.id,
        profile=profile,
        days_count=days_count,
        daily_time_limit_hours=daily_time_limit_hours,
        selected_interests=profile.interests,
        constraints={"return_to_start": start_location is not None},
        start_location=start_location,
        end_location=end_location,
        created_at=datetime.now(UTC),
    )


def _build_poi(
    *,
    poi_id: int,
    name: str,
    category: str,
    subcategory: str,
    latitude: float,
    longitude: float,
    description: str,
    average_cost_rub: int,
    estimated_visit_minutes: int,
    popularity_score: float,
    data_quality_score: float,
    interests: list[str],
    osm_tags: dict[str, str],
) -> PointOfInterestResponse:
    return PointOfInterestResponse(
        id=poi_id,
        city_id=77,
        name=name,
        category=category,
        subcategory=subcategory,
        latitude=latitude,
        longitude=longitude,
        address=f"{name} address",
        description=description,
        opening_hours=None,
        website=None,
        phone=None,
        source="test",
        external_id=f"poi-{poi_id}",
        wikidata_id=None,
        wikipedia_title=None,
        wikipedia_url=None,
        wikimedia_commons=None,
        osm_tags=osm_tags,
        estimated_price_level="medium" if average_cost_rub > 0 else "free",
        average_cost_rub=average_cost_rub,
        estimated_visit_minutes=estimated_visit_minutes,
        popularity_score=popularity_score,
        data_quality_score=data_quality_score,
        interests=interests,
        interest_source="test",
        primary_image=None,
        images=[],
        source_links=[],
        data_freshness_days=5,
        last_enriched_at=None,
    )
