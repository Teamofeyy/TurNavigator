from __future__ import annotations

from dataclasses import dataclass
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

COMPROMISE_STRATEGY_WEIGHTS: dict[str, dict[str, float]] = {
    "balanced": {
        "interest_match": 0.35,
        "budget_match": 0.20,
        "route_convenience": 0.15,
        "pace_match": 0.15,
        "popularity_score": 0.10,
        "data_quality_score": 0.05,
    },
    "budget_first": {
        "interest_match": 0.28,
        "budget_match": 0.30,
        "route_convenience": 0.14,
        "pace_match": 0.12,
        "popularity_score": 0.09,
        "data_quality_score": 0.07,
    },
    "time_first": {
        "interest_match": 0.26,
        "budget_match": 0.14,
        "route_convenience": 0.24,
        "pace_match": 0.22,
        "popularity_score": 0.08,
        "data_quality_score": 0.06,
    },
    "experience_first": {
        "interest_match": 0.24,
        "budget_match": 0.10,
        "route_convenience": 0.10,
        "pace_match": 0.12,
        "popularity_score": 0.24,
        "data_quality_score": 0.20,
    },
}

TRUST_LEVEL_WEIGHT_DELTAS: dict[str, dict[str, float]] = {
    "low": {
        "interest_match": 0.05,
        "budget_match": 0.03,
        "popularity_score": -0.05,
        "data_quality_score": -0.03,
    },
    "medium": {},
    "high": {
        "interest_match": -0.06,
        "budget_match": -0.03,
        "popularity_score": 0.05,
        "data_quality_score": 0.04,
    },
}

GOAL_CATEGORY_HINTS: dict[str, list[str]] = {
    "discover_local_culture": ["culture", "history", "architecture"],
    "photo_spots": ["architecture", "nature", "history", "culture"],
}

TIME_WINDOW_CATEGORY_FIT: dict[str, dict[str, float]] = {
    "morning": {
        "food": 0.95,
        "nature": 0.85,
        "history": 0.8,
        "culture": 0.75,
        "shopping": 0.55,
        "nightlife": 0.05,
    },
    "afternoon": {
        "culture": 0.9,
        "history": 0.88,
        "shopping": 0.82,
        "architecture": 0.8,
        "food": 0.7,
        "nightlife": 0.15,
    },
    "evening": {
        "nightlife": 1.0,
        "food": 0.92,
        "entertainment": 0.9,
        "architecture": 0.72,
        "culture": 0.55,
        "history": 0.5,
    },
}

PHOTO_SPOT_KEYWORDS = {
    "view",
    "panorama",
    "lookout",
    "observation",
    "riverfront",
    "embankment",
    "набереж",
    "панорам",
    "вид",
    "смотров",
}

QUIET_CATEGORIES = {"nature", "culture", "history", "architecture"}
LOUD_CATEGORIES = {"nightlife", "entertainment", "shopping"}
FAMILY_FRIENDLY_CATEGORIES = {"nature", "culture", "food", "history"}
STAIRS_KEYWORDS = {"stairs", "steps", "stair", "лестниц", "ступен"}
ACCESSIBLE_KEYWORDS = {"wheelchair", "accessible", "access", "безбарьер", "доступ"}

COMPROMISE_LABELS = {
    "balanced": "баланс интересов, времени и бюджета",
    "budget_first": "приоритет бюджета",
    "time_first": "приоритет времени и компактности",
    "experience_first": "приоритет впечатлений",
}

TRUST_LABELS = {
    "low": "низкий",
    "medium": "средний",
    "high": "высокий",
}


@dataclass(frozen=True)
class AdvancedProfileSignals:
    goal_alignment: float
    must_have_alignment: float
    avoid_penalty: float
    accessibility_fit: float | None
    time_window_fit: float | None
    exploration_fit: float


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
    fully_sorted = _sort_recommendations(scored, interests=interests)

    if trip_request.profile.compromise_strategy == "experience_first" or trip_request.profile.trust_level == "high":
        return fully_sorted

    if _allows_goal_driven_interleaving(trip_request) and len(intent_categories) > 1:
        return _interleave_by_category(
            fully_sorted,
            category_order=intent_categories,
        )

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


def _allows_goal_driven_interleaving(trip_request: TripRequestResponse) -> bool:
    return bool(trip_request.profile.goals) and trip_request.profile.trust_level != "low"


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
    advanced_signals = _advanced_profile_signals(
        poi=poi,
        trip_request=trip_request,
        matched_interests=matched_interests,
        factors=factors,
    )
    score = round(
        _clamp(
            _weighted_base_score(factors=factors, trip_request=trip_request)
            + _advanced_profile_adjustment(
                trip_request=trip_request,
                signals=advanced_signals,
            )
        ),
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
            signals=advanced_signals,
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
    for goal in _normalize_list(trip_request.profile.goals):
        for category in GOAL_CATEGORY_HINTS.get(goal, []):
            if category in seen:
                continue
            seen.add(category)
            categories.append(category)
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
    anchor_lat = city.latitude
    anchor_lon = city.longitude
    if trip_request.start_location is not None:
        anchor_lat = trip_request.start_location.latitude
        anchor_lon = trip_request.start_location.longitude

    distance_km = _distance_km(anchor_lat, anchor_lon, poi.latitude, poi.longitude)
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


def _weighted_base_score(
    *,
    factors: RecommendationFactors,
    trip_request: TripRequestResponse,
) -> float:
    weights = _strategy_weights(trip_request)
    factor_values = factors.model_dump()
    return sum(weights[name] * factor_values[name] for name in weights)


def _strategy_weights(trip_request: TripRequestResponse) -> dict[str, float]:
    weights = dict(
        COMPROMISE_STRATEGY_WEIGHTS.get(
            trip_request.profile.compromise_strategy,
            COMPROMISE_STRATEGY_WEIGHTS["balanced"],
        )
    )
    for name, delta in TRUST_LEVEL_WEIGHT_DELTAS.get(trip_request.profile.trust_level, {}).items():
        weights[name] = max(0.01, weights[name] + delta)
    total = sum(weights.values())
    return {name: value / total for name, value in weights.items()}


def _advanced_profile_signals(
    *,
    poi: PointOfInterestResponse,
    trip_request: TripRequestResponse,
    matched_interests: list[str],
    factors: RecommendationFactors,
) -> AdvancedProfileSignals:
    return AdvancedProfileSignals(
        goal_alignment=_goal_alignment_score(
            poi=poi,
            trip_request=trip_request,
            factors=factors,
        ),
        must_have_alignment=_keyword_alignment_score(
            poi=poi,
            keywords=trip_request.profile.must_have,
        ),
        avoid_penalty=_keyword_alignment_score(
            poi=poi,
            keywords=trip_request.profile.avoid,
        ),
        accessibility_fit=_accessibility_fit_score(
            poi=poi,
            trip_request=trip_request,
        ),
        time_window_fit=_time_window_fit_score(
            poi=poi,
            trip_request=trip_request,
        ),
        exploration_fit=_exploration_fit_score(
            poi=poi,
            trip_request=trip_request,
            matched_interests=matched_interests,
        ),
    )


def _goal_alignment_score(
    *,
    poi: PointOfInterestResponse,
    trip_request: TripRequestResponse,
    factors: RecommendationFactors,
) -> float:
    goals = _normalize_list(trip_request.profile.goals)
    if not goals:
        return 0.0

    blob = _poi_blob(poi)
    scores: list[float] = []
    selected_interests = set(_trip_interests(trip_request))
    for goal in goals:
        if goal == "discover_local_culture":
            scores.append(1.0 if poi.category in {"culture", "history", "architecture"} else 0.15)
        elif goal == "optimize_budget":
            scores.append(factors.budget_match)
        elif goal == "minimize_transfers":
            scores.append(factors.route_convenience)
        elif goal == "maximize_variety":
            if poi.category not in selected_interests and len(set(poi.interests)) >= 2:
                scores.append(1.0)
            elif poi.category not in selected_interests:
                scores.append(0.8)
            else:
                scores.append(0.35)
        elif goal == "photo_spots":
            photo_score = 1.0 if poi.category in {"architecture", "nature", "history", "culture"} else 0.25
            if any(keyword in blob for keyword in PHOTO_SPOT_KEYWORDS):
                photo_score = max(photo_score, 1.0)
            scores.append(photo_score)
        else:
            scores.append(0.0)

    return round(sum(scores) / len(scores), 4)


def _keyword_alignment_score(
    *,
    poi: PointOfInterestResponse,
    keywords: list[str],
) -> float:
    normalized_keywords = _normalize_list(keywords)
    if not normalized_keywords:
        return 0.0

    matches = [
        1.0 if _poi_matches_phrase(poi=poi, phrase=keyword) else 0.0
        for keyword in normalized_keywords
    ]
    return round(sum(matches) / len(matches), 4)


def _accessibility_fit_score(
    *,
    poi: PointOfInterestResponse,
    trip_request: TripRequestResponse,
) -> float | None:
    needs = _normalize_list(trip_request.profile.accessibility_needs)
    if not needs:
        return None

    blob = _poi_blob(poi)
    scores: list[float] = []
    for need in needs:
        if need == "wheelchair_access":
            if any(keyword in blob for keyword in STAIRS_KEYWORDS):
                scores.append(0.05)
            elif any(keyword in blob for keyword in ACCESSIBLE_KEYWORDS):
                scores.append(1.0)
            elif poi.category in {"food", "culture", "shopping"}:
                scores.append(0.7)
            else:
                scores.append(0.45)
        elif need == "quiet_places":
            if poi.category in QUIET_CATEGORIES:
                scores.append(0.95)
            elif poi.category in LOUD_CATEGORIES:
                scores.append(0.1)
            else:
                scores.append(0.45)
        elif need == "family_friendly":
            scores.append(0.9 if poi.category in FAMILY_FRIENDLY_CATEGORIES else 0.25)
        elif need == "rest_breaks":
            if poi.category in {"food", "nature"} or poi.estimated_visit_minutes <= 75:
                scores.append(0.9)
            elif poi.estimated_visit_minutes >= 150:
                scores.append(0.25)
            else:
                scores.append(0.55)
        else:
            scores.append(0.5)

    return round(sum(scores) / len(scores), 4)


def _time_window_fit_score(
    *,
    poi: PointOfInterestResponse,
    trip_request: TripRequestResponse,
) -> float | None:
    windows = _normalize_list(trip_request.profile.preferred_time_windows)
    if not windows:
        return None

    scores = [
        TIME_WINDOW_CATEGORY_FIT.get(window, {}).get(poi.category, 0.4)
        for window in windows
    ]
    return round(max(scores), 4)


def _exploration_fit_score(
    *,
    poi: PointOfInterestResponse,
    trip_request: TripRequestResponse,
    matched_interests: list[str],
) -> float:
    if matched_interests:
        return 0.0
    if _goal_alignment_score(
        poi=poi,
        trip_request=trip_request,
        factors=RecommendationFactors(
            interest_match=0.0,
            budget_match=0.0,
            route_convenience=0.0,
            pace_match=0.0,
            popularity_score=poi.popularity_score,
            data_quality_score=poi.data_quality_score,
        ),
    ) <= 0.5:
        return 0.0
    return 1.0 if poi.data_quality_score >= 0.7 or poi.popularity_score >= 0.7 else 0.5


def _advanced_profile_adjustment(
    *,
    trip_request: TripRequestResponse,
    signals: AdvancedProfileSignals,
) -> float:
    adjustment = (0.12 * signals.goal_alignment) + (0.14 * signals.must_have_alignment)
    adjustment -= 0.25 * signals.avoid_penalty

    if signals.accessibility_fit is not None:
        adjustment += 0.12 * (signals.accessibility_fit - 0.5)
    if signals.time_window_fit is not None:
        adjustment += 0.06 * (signals.time_window_fit - 0.5)

    if trip_request.profile.trust_level == "low":
        adjustment -= 0.07 * signals.exploration_fit
    elif trip_request.profile.trust_level == "high":
        adjustment += 0.08 * signals.exploration_fit
        adjustment += 0.05 * signals.goal_alignment

    if trip_request.profile.compromise_strategy == "experience_first":
        adjustment += 0.06 * signals.goal_alignment
        adjustment += 0.05 * signals.exploration_fit
    elif trip_request.profile.compromise_strategy == "budget_first":
        adjustment -= 0.04 * signals.exploration_fit

    return adjustment


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
    anchor_lat = city.latitude
    anchor_lon = city.longitude
    if trip_request.start_location is not None:
        anchor_lat = trip_request.start_location.latitude
        anchor_lon = trip_request.start_location.longitude
    distance_km = _distance_km(anchor_lat, anchor_lon, poi.latitude, poi.longitude)
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
    signals: AdvancedProfileSignals,
) -> str:
    if trip_request.profile.explanation_level == "short":
        short_parts = []
        if matched_interests:
            short_parts.append(f"совпадает с интересами: {', '.join(matched_interests)}")
        if signals.must_have_alignment > 0:
            short_parts.append("поддерживает must-have сценарии")
        if signals.accessibility_fit is not None and signals.accessibility_fit >= 0.7:
            short_parts.append("учитывает требования доступности")
        if signals.time_window_fit is not None and signals.time_window_fit >= 0.7:
            short_parts.append("хорошо ложится в предпочитаемое время дня")
        if not short_parts:
            short_parts.append("подходит по бюджету, темпу и расположению")
        return f"Объект «{poi.name}» рекомендован, потому что " + "; ".join(short_parts) + "."

    parts = []
    if matched_interests:
        parts.append(f"совпадает с интересами: {', '.join(matched_interests)}")
    else:
        parts.append("добавляет разнообразие к маршруту")

    if signals.goal_alignment > 0.55 and trip_request.profile.goals:
        parts.append(
            "поддерживает цели поездки: "
            + ", ".join(_normalize_list(trip_request.profile.goals))
        )
    if signals.must_have_alignment > 0:
        parts.append("совпадает с одним из must-have требований пользователя")
    if signals.avoid_penalty > 0:
        parts.append("частично конфликтует с avoid-ограничениями и поэтому получает штраф")

    if constraint_status.budget == "within_budget":
        parts.append(f"не превышает бюджет, ориентировочная стоимость {poi.average_cost_rub} руб.")
    else:
        parts.append(f"может выйти за бюджет, ориентировочная стоимость {poi.average_cost_rub} руб.")

    if constraint_status.distance == "near_city_center":
        parts.append("удобно расположен относительно точки старта")
    else:
        parts.append("может потребовать транспорт или более длинный переход")

    if signals.accessibility_fit is not None:
        if signals.accessibility_fit >= 0.7:
            parts.append("хорошо поддерживает выбранные accessibility needs")
        elif signals.accessibility_fit <= 0.3:
            parts.append("может хуже подходить под выбранные accessibility needs")

    if signals.time_window_fit is not None and signals.time_window_fit >= 0.7:
        parts.append("категория хорошо вписывается в предпочитаемые окна времени")

    parts.append(f"оценка совпадения по интересам {round(factors.interest_match, 2)}")
    parts.append(
        "стратегия компромиссов: "
        + COMPROMISE_LABELS.get(
            trip_request.profile.compromise_strategy,
            COMPROMISE_LABELS["balanced"],
        )
    )
    parts.append(
        "уровень доверия системе: "
        + TRUST_LABELS.get(trip_request.profile.trust_level, TRUST_LABELS["medium"])
    )
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
    return set(
        _normalize_list(
            [
                poi.category,
                poi.subcategory,
                *poi.interests,
                *poi.osm_tags.keys(),
                *poi.osm_tags.values(),
            ]
        )
    )


def _poi_blob(poi: PointOfInterestResponse) -> str:
    parts = [
        poi.name,
        poi.category,
        poi.subcategory,
        poi.address,
        poi.description,
        *poi.interests,
        *poi.osm_tags.keys(),
        *poi.osm_tags.values(),
    ]
    return " ".join(_normalize_text(part) for part in parts if part.strip())


def _poi_matches_phrase(*, poi: PointOfInterestResponse, phrase: str) -> bool:
    normalized_phrase = _normalize_text(phrase)
    if not normalized_phrase:
        return False

    blob = _poi_blob(poi)
    if normalized_phrase in blob:
        return True

    words = [word for word in normalized_phrase.split() if word]
    if not words:
        return False
    return all(word in blob for word in words)


def _normalize_list(values: list[str]) -> list[str]:
    return [value.strip().lower() for value in values if value.strip()]


def _normalize_text(value: str) -> str:
    return value.strip().lower().replace("_", " ").replace("-", " ")


def _normalize_optional_set(values: list[str] | None) -> set[str] | None:
    if values is None:
        return None
    return set(_normalize_list(values))


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    )
    return 2 * earth_radius_km * asin(sqrt(a))
