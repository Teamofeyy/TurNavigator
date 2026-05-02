from __future__ import annotations

import argparse
from datetime import UTC, datetime

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import POI


SHOP_SUBCATEGORY_BY_OSM_VALUE: dict[str, str] = {
    "mall": "mall",
    "department_store": "department_store",
    "clothes": "clothes_store",
    "shoes": "shoes_store",
    "sports": "sports_store",
    "jewelry": "jewelry_store",
    "cosmetics": "cosmetics_store",
    "electronics": "electronics_store",
    "mobile_phone": "mobile_phone_store",
    "bag": "bags_store",
    "optician": "optician",
    "books": "bookstore",
}

SHOPPING_POPULARITY_FLOORS: dict[str, float] = {
    "mall": 0.82,
    "department_store": 0.76,
    "clothes_store": 0.68,
    "shoes_store": 0.68,
    "sports_store": 0.66,
    "jewelry_store": 0.64,
    "cosmetics_store": 0.64,
    "electronics_store": 0.64,
    "mobile_phone_store": 0.62,
    "bags_store": 0.62,
    "bookstore": 0.6,
}

UTILITY_FOOD_SUBCATEGORIES = {"market", "marketplace", "supermarket", "convenience_store"}
FOOD_INTERESTS = {"food", "coffee", "dessert"}
COMMERCE_INTERESTS = {"shopping"}
NIGHTLIFE_INTERESTS = {"nightlife"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Repair imported POI categories after taxonomy changes."
    )
    parser.add_argument("--city-id", type=int, default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    changed = 0
    markets_reclassified = 0
    shopping_normalized = 0
    interests_cleaned = 0

    with SessionLocal() as session:
        statement = select(POI).order_by(POI.city_id.asc(), POI.id.asc())
        if args.city_id is not None:
            statement = statement.where(POI.city_id == args.city_id)

        for poi in session.scalars(statement).all():
            original = _snapshot(poi)

            if _is_marketplace(poi):
                poi.category = "food"
                poi.subcategory = "market"
                poi.interests = sorted(
                    (
                        set(poi.interests or [])
                        - COMMERCE_INTERESTS
                        - FOOD_INTERESTS
                    )
                    | {"local_identity", "budget_control"}
                )
                poi.estimated_visit_minutes = max(poi.estimated_visit_minutes or 0, 45)
                poi.popularity_score = min(poi.popularity_score, 0.58)
                markets_reclassified += 1

            elif poi.category == "shopping":
                normalized_subcategory = _shopping_subcategory(poi)
                if normalized_subcategory:
                    poi.subcategory = normalized_subcategory
                poi.interests = sorted(set(poi.interests or []) | {"shopping"})
                poi.estimated_visit_minutes = _shopping_visit_minutes(poi.subcategory)
                poi.popularity_score = max(
                    poi.popularity_score,
                    SHOPPING_POPULARITY_FLOORS.get(poi.subcategory, 0.56),
                )
                if poi.website or poi.phone or poi.opening_hours:
                    poi.data_quality_score = max(poi.data_quality_score, 0.6)
                shopping_normalized += 1

            cleaned_interests = _clean_misleading_interests(
                category=poi.category,
                subcategory=poi.subcategory,
                interests=poi.interests or [],
            )
            if cleaned_interests != sorted(poi.interests or []):
                poi.interests = cleaned_interests
                interests_cleaned += 1

            if _snapshot(poi) != original:
                poi.last_enriched_at = datetime.now(UTC)
                changed += 1

        session.commit()

    print(
        "Catalog categories repaired: "
        f"changed={changed}, markets_reclassified={markets_reclassified}, "
        f"shopping_normalized={shopping_normalized}, "
        f"interests_cleaned={interests_cleaned}"
    )


def _snapshot(poi: POI) -> tuple:
    return (
        poi.category,
        poi.subcategory,
        tuple(poi.interests or []),
        poi.estimated_visit_minutes,
        poi.popularity_score,
        poi.data_quality_score,
    )


def _is_marketplace(poi: POI) -> bool:
    tags = poi.osm_tags or {}
    name = (poi.name or "").lower()
    return (
        poi.subcategory in {"market", "marketplace"}
        or tags.get("amenity") == "marketplace"
        or tags.get("shop") == "marketplace"
        or "рынок" in name
    )


def _shopping_subcategory(poi: POI) -> str | None:
    tags = poi.osm_tags or {}
    shop_value = str(tags.get("shop") or "").strip().lower()
    if shop_value in SHOP_SUBCATEGORY_BY_OSM_VALUE:
        return SHOP_SUBCATEGORY_BY_OSM_VALUE[shop_value]
    if poi.subcategory == "shopping_mall":
        return "mall"
    return poi.subcategory


def _shopping_visit_minutes(subcategory: str) -> int:
    if subcategory == "mall":
        return 120
    if subcategory in {"department_store", "bookstore"}:
        return 60
    return 45


def _clean_misleading_interests(
    *,
    category: str,
    subcategory: str,
    interests: list[str],
) -> list[str]:
    cleaned = set(interests)

    if category not in {"food", "nightlife"}:
        cleaned -= FOOD_INTERESTS
    if category != "shopping":
        cleaned -= COMMERCE_INTERESTS
    if category != "nightlife":
        cleaned -= NIGHTLIFE_INTERESTS
    if category == "food" and subcategory in UTILITY_FOOD_SUBCATEGORIES:
        cleaned -= FOOD_INTERESTS

    if category == "food" and subcategory not in UTILITY_FOOD_SUBCATEGORIES:
        cleaned.add("food")
    if category == "shopping":
        cleaned.add("shopping")
    if category == "nightlife":
        cleaned.add("nightlife")

    return sorted(cleaned)


if __name__ == "__main__":
    main()
