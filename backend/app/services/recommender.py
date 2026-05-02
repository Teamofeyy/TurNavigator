from math import asin, cos, radians, sin, sqrt

from app.schemas.city import CityResponse
from app.schemas.planning import (
    ConstraintStatus,
    RecommendationFactors,
    RecommendationResponse,
    TripRequestResponse,
)
from app.schemas.poi import PointOfInterestResponse
from app.services.catalog_service import list_city_pois

PRICE_LEVEL_FIT: dict[str, dict[str, float]] = {
    "low": {"free": 1.0, "low": 0.95, "medium": 0.45, "high": 0.1},
    "medium": {"free": 0.9, "low": 1.0, "medium": 0.85, "high": 0.45},
    "high": {"free": 0.75, "low": 0.85, "medium": 0.95, "high": 1.0},
}

PACE_VISIT_LIMITS: dict[str, tuple[int, int]] = {
    "relaxed": (0, 90),
    "moderate": (30, 150),
    "intensive": (45, 240),
}

PRIMARY_INTEREST_CATEGORIES = {
    "history",
    "culture",
    "food",
    "nature",
    "architecture",
    "entertainment",
    "shopping",
    "nightlife",
}

MARKET_SUBCATEGORIES = {"market", "marketplace"}

INTEREST_SUBCATEGORY_WEIGHTS: dict[str, dict[str, float]] = {
    "food": {
        "restaurant": 1.0,
        "cafe": 0.95,
        "confectionery_cafe": 0.92,
        "confectionery": 0.88,
        "bakery": 0.86,
        "food_court": 0.72,
        "fast_food": 0.58,
        "bar": 0.48,
        "pub": 0.48,
        "biergarten": 0.48,
        "market": 0.0,
        "marketplace": 0.0,
        "supermarket": 0.0,
        "convenience_store": 0.0,
    },
    "nightlife": {
        "nightclub": 1.0,
        "bar": 0.96,
        "pub": 0.94,
        "biergarten": 0.9,
    },
    "shopping": {
        "mall": 1.0,
        "department_store": 0.95,
        "clothes_store": 0.9,
        "shoes_store": 0.9,
        "sports_store": 0.88,
        "jewelry_store": 0.86,
        "cosmetics_store": 0.86,
        "electronics_store": 0.84,
        "mobile_phone_store": 0.8,
        "bags_store": 0.8,
        "optician": 0.74,
        "bookstore": 0.72,
        "gift_shop": 0.68,
        "souvenir_shop": 0.66,
        "shop": 0.64,
        "market": 0.0,
        "marketplace": 0.0,
    },
}


def generate_recommendations(
    trip_request: TripRequestResponse,
    city: CityResponse,
    limit: int,
    include_accommodation: bool,
    include_categories: list[str] | None = None,
    exclude_categories: list[str] | None = None,
) -> tuple[list[RecommendationResponse], int]:
    include_set = _normalize_optional_set(include_categories)
    exclude_set = set(_normalize_list(exclude_categories or []))
    intent_categories = _intent_categories(trip_request)
    if not include_accommodation:
        exclude_set.add("accommodation")

    catalog_limit = min(max(city.pois_count, limit * 20, 100), 500)
    candidates = [
        poi
        for poi in list_city_pois(city_id=trip_request.city_id, limit=catalog_limit, offset=0)
        if _is_allowed_category(poi, include_set, exclude_set)
        and _matches_intent_categories(poi=poi, intent_categories=intent_categories)
    ]

    scored = [
        _score_poi(
            poi=poi,
            city=city,
            trip_request=trip_request,
        )
        for poi in candidates
    ]
    recommendations = _rank_recommendations(
        scored,
        trip_request=trip_request,
        intent_categories=intent_categories,
    )
    for index, recommendation in enumerate(recommendations, start=1):
        recommendation.rank = index
    return recommendations[:limit], len(candidates)


def _rank_recommendations(
    scored: list[RecommendationResponse],
    *,
    trip_request: TripRequestResponse,
    intent_categories: list[str],
) -> list[RecommendationResponse]:
    interests = _trip_interests(trip_request)
    relevant = [item for item in scored if item.factors.interest_match > 0]
    fallback = [item for item in scored if item.factors.interest_match <= 0]
    if len(intent_categories) > 1:
        return [
            *_interleave_by_category(
                _sort_recommendations(relevant, interests=interests),
                category_order=intent_categories,
            ),
            *_sort_recommendations(fallback, interests=interests),
        ]
    return [
        *_sort_recommendations(relevant, interests=interests),
        *_sort_recommendations(fallback, interests=interests),
    ]


def _interleave_by_category(
    items: list[RecommendationResponse],
    *,
    category_order: list[str],
) -> list[RecommendationResponse]:
    buckets = {
        category: [item for item in items if item.poi.category == category]
        for category in category_order
    }
    item_ids = {id(item) for bucket in buckets.values() for item in bucket}
    other_items = [item for item in items if id(item) not in item_ids]

    interleaved: list[RecommendationResponse] = []
    while any(buckets.values()):
        for category in category_order:
            bucket = buckets[category]
            if bucket:
                interleaved.append(bucket.pop(0))

    return [*interleaved, *other_items]


def _sort_recommendations(
    items: list[RecommendationResponse],
    *,
    interests: list[str],
) -> list[RecommendationResponse]:
    return sorted(
        items,
        key=lambda item: (
            item.score,
            _topic_priority_score(item.poi, interests),
            bool(item.poi.primary_image),
            item.poi.data_quality_score,
            item.poi.popularity_score,
        ),
        reverse=True,
    )


def _score_poi(
    poi: PointOfInterestResponse,
    city: CityResponse,
    trip_request: TripRequestResponse,
) -> RecommendationResponse:
    interests = _trip_interests(trip_request)
    matched_interests = _matched_interests(poi=poi, interests=interests)
    factors = RecommendationFactors(
        interest_match=_interest_match_score(poi=poi, interests=interests),
        budget_match=_budget_match_score(poi=poi, trip_request=trip_request),
        route_convenience=_route_convenience_score(poi=poi, city=city, trip_request=trip_request),
        pace_match=_pace_match_score(poi=poi, trip_request=trip_request),
        popularity_score=poi.popularity_score,
        data_quality_score=poi.data_quality_score,
    )
    score = round(
        (0.35 * factors.interest_match)
        + (0.20 * factors.budget_match)
        + (0.15 * factors.route_convenience)
        + (0.15 * factors.pace_match)
        + (0.10 * factors.popularity_score)
        + (0.05 * factors.data_quality_score),
        4,
    )
    constraint_status = _constraint_status(poi=poi, city=city, trip_request=trip_request)
    return RecommendationResponse(
        poi_id=poi.id,
        name=poi.name,
        category=poi.category,
        score=score,
        rank=1,
        matched_interests=matched_interests,
        factors=factors,
        constraint_status=constraint_status,
        explanation=_build_explanation(
            poi=poi,
            trip_request=trip_request,
            matched_interests=matched_interests,
            factors=factors,
            constraint_status=constraint_status,
        ),
        poi=poi,
    )


def _trip_interests(trip_request: TripRequestResponse) -> list[str]:
    return _normalize_list(trip_request.selected_interests or trip_request.profile.interests)


def _intent_categories(trip_request: TripRequestResponse) -> list[str]:
    seen: set[str] = set()
    categories: list[str] = []
    for interest in _trip_interests(trip_request):
        if interest not in PRIMARY_INTEREST_CATEGORIES or interest in seen:
            continue
        seen.add(interest)
        categories.append(interest)
    return categories


def _matched_interests(poi: PointOfInterestResponse, interests: list[str]) -> list[str]:
    return sorted(
        {
            interest
            for interest in set(interests)
            if _single_interest_match_score(poi=poi, interest=interest) > 0
        }
    )


def _interest_match_score(poi: PointOfInterestResponse, interests: list[str]) -> float:
    if not interests:
        return 0
    normalized_interests = sorted(set(interests))
    if not normalized_interests:
        return 0
    return round(
        sum(
            _single_interest_match_score(poi=poi, interest=interest)
            for interest in normalized_interests
        )
        / len(normalized_interests),
        4,
    )


def _single_interest_match_score(
    *,
    poi: PointOfInterestResponse,
    interest: str,
) -> float:
    normalized_interest = interest.strip().lower()
    poi_terms = _poi_terms(poi)

    if normalized_interest == "shopping" and poi.subcategory in MARKET_SUBCATEGORIES:
        return 0.0

    subcategory_weight = INTEREST_SUBCATEGORY_WEIGHTS.get(
        normalized_interest,
        {},
    ).get(poi.subcategory)
    if subcategory_weight is not None and (
        normalized_interest in poi_terms or poi.category == normalized_interest
    ):
        return subcategory_weight

    if normalized_interest in poi_terms:
        return 1.0
    if poi.category == normalized_interest:
        return 0.85
    return 0.0


def _topic_priority_score(poi: PointOfInterestResponse, interests: list[str]) -> float:
    if not interests:
        return 0.0
    return max(
        (
            _single_interest_match_score(poi=poi, interest=interest)
            for interest in interests
        ),
        default=0.0,
    )


def _matches_intent_categories(
    *,
    poi: PointOfInterestResponse,
    intent_categories: list[str],
) -> bool:
    if not intent_categories:
        return True
    return poi.category in set(intent_categories)


def _budget_match_score(poi: PointOfInterestResponse, trip_request: TripRequestResponse) -> float:
    price_fit = PRICE_LEVEL_FIT[trip_request.profile.budget_level].get(
        poi.estimated_price_level,
        0.5,
    )
    max_budget = trip_request.profile.max_budget
    if max_budget <= 0:
        cost_fit = 1.0 if poi.average_cost_rub == 0 else 0.25
    elif poi.average_cost_rub <= max_budget:
        cost_fit = 1.0
    else:
        cost_fit = max(0.0, min(1.0, max_budget / poi.average_cost_rub))
    return round((0.6 * price_fit) + (0.4 * cost_fit), 4)


def _route_convenience_score(
    poi: PointOfInterestResponse,
    city: CityResponse,
    trip_request: TripRequestResponse,
) -> float:
    distance_km = _distance_km(city.latitude, city.longitude, poi.latitude, poi.longitude)
    max_walk = max(1.0, trip_request.profile.max_walking_distance_km)
    if trip_request.profile.preferred_transport == "walking":
        return round(max(0.1, 1 - (distance_km / max_walk)), 4)
    return round(max(0.25, 1 - (distance_km / 20)), 4)


def _pace_match_score(poi: PointOfInterestResponse, trip_request: TripRequestResponse) -> float:
    min_minutes, max_minutes = PACE_VISIT_LIMITS[trip_request.profile.pace]
    visit_minutes = poi.estimated_visit_minutes
    if min_minutes <= visit_minutes <= max_minutes:
        return 1.0
    if visit_minutes == 0:
        return 0.7
    distance_from_range = min(abs(visit_minutes - min_minutes), abs(visit_minutes - max_minutes))
    return round(max(0.2, 1 - (distance_from_range / 180)), 4)


def _constraint_status(
    poi: PointOfInterestResponse,
    city: CityResponse,
    trip_request: TripRequestResponse,
) -> ConstraintStatus:
    budget_status = (
        "within_budget"
        if poi.average_cost_rub <= trip_request.profile.max_budget
        else "over_budget"
    )
    pace_status = f"fits_{trip_request.profile.pace}_pace"
    distance_km = _distance_km(city.latitude, city.longitude, poi.latitude, poi.longitude)
    distance_status = (
        "near_city_center"
        if distance_km <= trip_request.profile.max_walking_distance_km
        else "requires_transport"
    )
    return ConstraintStatus(
        budget=budget_status,
        pace=pace_status,
        distance=distance_status,
    )


def _build_explanation(
    poi: PointOfInterestResponse,
    trip_request: TripRequestResponse,
    matched_interests: list[str],
    factors: RecommendationFactors,
    constraint_status: ConstraintStatus,
) -> str:
    if trip_request.profile.explanation_level == "short":
        if matched_interests:
            return f"Объект «{poi.name}» подходит по интересам: {', '.join(matched_interests)}."
        return f"Объект «{poi.name}» подходит по бюджету, темпу и расположению."

    parts = []
    if matched_interests:
        parts.append(f"совпадает с интересами: {', '.join(matched_interests)}")
    else:
        parts.append("добавляет разнообразие к маршруту")
    if constraint_status.budget == "within_budget":
        parts.append(f"не превышает бюджет, ориентировочная стоимость {poi.average_cost_rub} руб.")
    else:
        parts.append(f"может выйти за бюджет, ориентировочная стоимость {poi.average_cost_rub} руб.")
    if constraint_status.distance == "near_city_center":
        parts.append("удобно расположен относительно центра города")
    else:
        parts.append("может потребовать транспорт")
    parts.append(f"оценка полезности: {round(factors.interest_match, 2)} по интересам")
    return f"Объект «{poi.name}» рекомендован, потому что " + "; ".join(parts) + "."


def _is_allowed_category(
    poi: PointOfInterestResponse,
    include_set: set[str] | None,
    exclude_set: set[str],
) -> bool:
    if include_set is not None and poi.category not in include_set:
        return False
    return poi.category not in exclude_set


def _poi_terms(poi: PointOfInterestResponse) -> set[str]:
    return set(_normalize_list([poi.category, poi.subcategory, *poi.interests]))


def _normalize_list(values: list[str]) -> list[str]:
    return [value.strip().lower() for value in values if value.strip()]


def _normalize_optional_set(values: list[str] | None) -> set[str] | None:
    if values is None:
        return None
    return set(_normalize_list(values))


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    )
    return 2 * earth_radius_km * asin(sqrt(a))
