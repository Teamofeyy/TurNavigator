from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

from app.services.media_urls import normalize_poi_image_url


CATEGORY_INTEREST_MAP: dict[str, set[str]] = {
    "history": {"history", "culture"},
    "culture": {"culture", "history", "indoor"},
    "food": {"food"},
    "nature": {"nature", "walking", "outdoor"},
    "architecture": {"architecture", "history", "culture"},
    "entertainment": {"entertainment"},
    "shopping": {"shopping"},
    "nightlife": {"nightlife", "entertainment"},
    "accommodation": {"comfort", "rest"},
}

SUBCATEGORY_INTEREST_MAP: dict[str, set[str]] = {
    "museum": {"history", "culture", "indoor"},
    "museum_complex": {"history", "culture", "architecture"},
    "theatre": {"culture", "entertainment", "indoor"},
    "park": {"nature", "walking", "outdoor"},
    "viewpoint": {"nature", "panorama", "walking", "outdoor"},
    "cathedral": {"architecture", "history", "culture"},
    "kremlin": {"history", "architecture", "culture"},
    "market": {"food", "local_identity", "budget_control"},
    "marketplace": {"food", "local_identity", "budget_control"},
    "restaurant": {"food"},
    "cafe": {"food", "coffee"},
    "confectionery_cafe": {"food", "dessert", "coffee"},
    "food_court": {"food"},
    "bakery": {"food", "dessert", "coffee"},
    "confectionery": {"food", "dessert"},
    "bar": {"nightlife", "food"},
    "pub": {"nightlife", "food"},
    "biergarten": {"nightlife", "food"},
    "nightclub": {"nightlife", "entertainment"},
    "mall": {"shopping"},
    "department_store": {"shopping"},
    "gift_shop": {"shopping", "local_identity"},
    "souvenir_shop": {"shopping", "local_identity"},
    "clothes_store": {"shopping"},
    "shoes_store": {"shopping"},
    "sports_store": {"shopping"},
    "jewelry_store": {"shopping"},
    "cosmetics_store": {"shopping"},
    "electronics_store": {"shopping"},
    "mobile_phone_store": {"shopping"},
    "bags_store": {"shopping"},
    "optician": {"shopping"},
    "bookstore": {"shopping", "culture"},
    "hotel": {"comfort", "rest"},
    "hostel": {"budget", "rest"},
    "embankment": {"walking", "outdoor", "panorama"},
}

OSM_TAG_INTEREST_MAP: dict[tuple[str, str], set[str]] = {
    ("tourism", "museum"): {"history", "culture", "indoor"},
    ("tourism", "attraction"): {"culture", "history"},
    ("tourism", "viewpoint"): {"nature", "panorama", "walking", "outdoor"},
    ("tourism", "hotel"): {"comfort", "rest"},
    ("tourism", "hostel"): {"budget", "rest"},
    ("tourism", "guest_house"): {"rest", "comfort"},
    ("historic", "memorial"): {"history", "culture"},
    ("historic", "monument"): {"history", "culture"},
    ("historic", "castle"): {"history", "architecture", "culture"},
    ("amenity", "theatre"): {"culture", "entertainment", "indoor"},
    ("amenity", "arts_centre"): {"culture", "indoor"},
    ("amenity", "cafe"): {"food", "coffee"},
    ("amenity", "restaurant"): {"food"},
    ("amenity", "fast_food"): {"food"},
    ("amenity", "food_court"): {"food"},
    ("amenity", "ice_cream"): {"food", "dessert"},
    ("amenity", "bar"): {"nightlife", "food"},
    ("amenity", "pub"): {"nightlife", "food"},
    ("amenity", "biergarten"): {"nightlife", "food"},
    ("amenity", "nightclub"): {"nightlife", "entertainment"},
    ("amenity", "marketplace"): {"food", "local_identity", "budget_control"},
    ("leisure", "park"): {"nature", "walking", "outdoor"},
    ("leisure", "garden"): {"nature", "walking", "outdoor"},
    ("shop", "mall"): {"shopping"},
    ("shop", "marketplace"): {"food", "local_identity", "budget_control"},
    ("shop", "department_store"): {"shopping"},
    ("shop", "gift"): {"shopping", "local_identity"},
    ("shop", "souvenir"): {"shopping", "local_identity"},
    ("shop", "clothes"): {"shopping"},
    ("shop", "shoes"): {"shopping"},
    ("shop", "sports"): {"shopping"},
    ("shop", "jewelry"): {"shopping"},
    ("shop", "cosmetics"): {"shopping"},
    ("shop", "electronics"): {"shopping"},
    ("shop", "mobile_phone"): {"shopping"},
    ("shop", "bag"): {"shopping"},
    ("shop", "optician"): {"shopping"},
    ("shop", "books"): {"shopping", "culture"},
    ("shop", "supermarket"): {"food", "budget_control"},
    ("shop", "convenience"): {"food", "budget_control"},
    ("shop", "bakery"): {"food", "dessert"},
    ("shop", "confectionery"): {"food", "dessert"},
}

KEYWORD_INTEREST_MAP: dict[str, set[str]] = {
    "музей": {"history", "culture", "indoor"},
    "кремль": {"history", "architecture", "culture"},
    "театр": {"culture", "entertainment", "indoor"},
    "парк": {"nature", "walking", "outdoor"},
    "набереж": {"walking", "outdoor", "panorama"},
    "собор": {"architecture", "history", "culture"},
    "рынок": {"food", "local_identity", "budget_control"},
    "кафе": {"food", "coffee"},
    "ресторан": {"food"},
    "бар": {"nightlife", "food"},
    "паб": {"nightlife", "food"},
    "клуб": {"nightlife", "entertainment"},
    "кофей": {"food", "coffee"},
    "пекар": {"food", "dessert"},
    "магазин": {"shopping"},
    "торговый центр": {"shopping"},
    "тц": {"shopping"},
    "молл": {"shopping"},
    "одеж": {"shopping"},
    "обув": {"shopping"},
    "сувенир": {"shopping", "local_identity"},
    "отель": {"comfort", "rest"},
    "hotel": {"comfort", "rest"},
    "hostel": {"budget", "rest"},
    "museum": {"history", "culture", "indoor"},
    "park": {"nature", "walking", "outdoor"},
}


def enrich_seed_poi_record(record: dict[str, Any]) -> dict[str, Any]:
    normalized_record = dict(record)
    osm_tags = _coerce_string_dict(normalized_record.get("osm_tags"))
    normalized_record["osm_tags"] = osm_tags

    normalized_record["website"] = _normalize_website(
        normalized_record.get("website")
        or osm_tags.get("website")
        or osm_tags.get("contact:website")
    )
    normalized_record["phone"] = _normalize_phone(
        normalized_record.get("phone")
        or osm_tags.get("phone")
        or osm_tags.get("contact:phone")
    )
    normalized_record["opening_hours"] = (
        normalized_record.get("opening_hours")
        or osm_tags.get("opening_hours")
        or None
    )
    normalized_record["description"] = (
        normalized_record.get("description")
        or f"Точка интереса «{normalized_record.get('name', 'Без названия')}»."
    )

    manual_interests = _normalize_string_list(normalized_record.get("interests"))
    inferred_interests = infer_interests(
        category=normalized_record.get("category"),
        subcategory=normalized_record.get("subcategory"),
        osm_tags=osm_tags,
        name=normalized_record.get("name"),
        description=normalized_record.get("description"),
        existing_interests=manual_interests,
    )
    normalized_record["interests"] = inferred_interests
    normalized_record["interest_source"] = _build_interest_source(
        manual_interests=manual_interests,
        final_interests=inferred_interests,
    )

    normalized_record["wikipedia_title"] = normalized_record.get("wikipedia_title")
    normalized_record["wikipedia_url"] = normalized_record.get("wikipedia_url")
    normalized_record["wikimedia_commons"] = normalized_record.get("wikimedia_commons")
    normalized_record["primary_image"] = _normalize_primary_image(
        normalized_record.get("primary_image")
    )
    normalized_record["images"] = _normalize_images(
        normalized_record.get("images"),
        normalized_record["primary_image"],
    )
    normalized_record["source_links"] = _build_source_links(normalized_record)
    normalized_record["popularity_score"] = _clamp_score(
        normalized_record.get("popularity_score"),
        fallback=estimate_popularity_score(normalized_record),
    )
    normalized_record["data_quality_score"] = _clamp_score(
        normalized_record.get("data_quality_score"),
        fallback=compute_data_quality_score(normalized_record),
    )
    normalized_record["data_freshness_days"] = _safe_int(
        normalized_record.get("data_freshness_days"),
        fallback=30,
    )
    normalized_record["last_enriched_at"] = normalized_record.get("last_enriched_at") or datetime.now(
        UTC
    ).isoformat()
    return normalized_record


def infer_interests(
    *,
    category: str | None,
    subcategory: str | None,
    osm_tags: dict[str, str],
    name: str | None,
    description: str | None,
    existing_interests: list[str] | None = None,
) -> list[str]:
    interests: set[str] = set(_normalize_string_list(existing_interests or []))

    normalized_category = _normalize_token(category)
    normalized_subcategory = _normalize_token(subcategory)
    if normalized_category:
        interests.update(CATEGORY_INTEREST_MAP.get(normalized_category, set()))
    if normalized_subcategory:
        interests.update(SUBCATEGORY_INTEREST_MAP.get(normalized_subcategory, set()))

    for key, value in osm_tags.items():
        normalized_key = _normalize_token(key)
        normalized_value = _normalize_token(value)
        if not normalized_key or not normalized_value:
            continue
        interests.update(OSM_TAG_INTEREST_MAP.get((normalized_key, normalized_value), set()))

    haystack = " ".join(
        value
        for value in [
            name or "",
            description or "",
            category or "",
            subcategory or "",
            " ".join(osm_tags.values()),
        ]
        if value
    ).lower()
    for keyword, mapped_interests in KEYWORD_INTEREST_MAP.items():
        if keyword in haystack:
            interests.update(mapped_interests)

    if not interests and normalized_category:
        interests.add(normalized_category)

    return sorted(interests)


def estimate_popularity_score(record: dict[str, Any]) -> float:
    source_rating = _safe_int(record.get("source_rating"))
    if source_rating is not None:
        rating_map = {
            1: 0.55,
            2: 0.75,
            3: 0.9,
        }
        if source_rating in rating_map:
            return rating_map[source_rating]

    popularity_hints = 0.35
    if record.get("wikidata_id"):
        popularity_hints += 0.15
    if record.get("wikipedia_url") or record.get("wikipedia_title"):
        popularity_hints += 0.1
    if record.get("primary_image") or record.get("images"):
        popularity_hints += 0.08
    if record.get("website"):
        popularity_hints += 0.07
    if record.get("phone"):
        popularity_hints += 0.05
    if record.get("opening_hours"):
        popularity_hints += 0.05
    if record.get("category") in {"history", "culture", "nature"}:
        popularity_hints += 0.05
    return round(min(popularity_hints, 0.95), 2)


def compute_data_quality_score(record: dict[str, Any]) -> float:
    checks = [
        bool(record.get("description")),
        bool(record.get("website")),
        bool(record.get("phone")),
        bool(record.get("opening_hours")),
        bool(record.get("wikidata_id")),
        bool(record.get("wikipedia_url") or record.get("wikipedia_title")),
        bool(record.get("primary_image") or record.get("images")),
        bool(record.get("source_links")),
        bool(record.get("interests")),
        record.get("latitude") is not None and record.get("longitude") is not None,
    ]
    return round(sum(checks) / len(checks), 2)


def _build_interest_source(
    *,
    manual_interests: list[str],
    final_interests: list[str],
) -> str:
    manual_set = set(manual_interests)
    final_set = set(final_interests)
    if not manual_set:
        return "automatic"
    if final_set == manual_set:
        return "manual"
    return "manual+automatic"


def _build_source_links(record: dict[str, Any]) -> list[dict[str, Any]]:
    source_links: list[dict[str, Any]] = []
    source = str(record.get("source") or "unknown").strip().lower()
    external_id = str(record.get("external_id") or "").strip()
    if source and external_id:
        source_links.append(
            {
                "provider": source,
                "external_id": external_id,
                "url": None,
                "license": None,
                "last_synced_at": record.get("last_enriched_at"),
            }
        )

    wikidata_id = record.get("wikidata_id")
    if wikidata_id:
        source_links.append(
            {
                "provider": "wikidata",
                "external_id": wikidata_id,
                "url": f"https://www.wikidata.org/wiki/{wikidata_id}",
                "license": "CC0",
                "last_synced_at": record.get("last_enriched_at"),
            }
        )

    wikipedia_title = record.get("wikipedia_title")
    wikipedia_url = record.get("wikipedia_url")
    if wikipedia_title or wikipedia_url:
        source_links.append(
            {
                "provider": "wikipedia",
                "external_id": wikipedia_title or wikipedia_url,
                "url": wikipedia_url,
                "license": "CC BY-SA",
                "last_synced_at": record.get("last_enriched_at"),
            }
        )

    wikimedia_commons = record.get("wikimedia_commons")
    if wikimedia_commons:
        source_links.append(
            {
                "provider": "wikimedia_commons",
                "external_id": wikimedia_commons,
                "url": f"https://commons.wikimedia.org/wiki/{wikimedia_commons}",
                "license": None,
                "last_synced_at": record.get("last_enriched_at"),
            }
        )

    return source_links


def _normalize_primary_image(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    provider = str(value.get("provider") or "").strip().lower()
    original_url = normalize_poi_image_url(_normalize_website(value.get("original_url")))
    thumbnail_url = normalize_poi_image_url(_normalize_website(value.get("thumbnail_url")))
    source_page_url = _normalize_website(value.get("source_page_url"))
    if not provider and not original_url and not thumbnail_url and not source_page_url:
        return None
    return {
        "provider": provider or "unknown",
        "original_url": original_url,
        "thumbnail_url": thumbnail_url,
        "source_page_url": source_page_url,
        "license": value.get("license"),
        "author": value.get("author"),
        "attribution_text": value.get("attribution_text"),
        "width": _safe_int(value.get("width")),
        "height": _safe_int(value.get("height")),
        "is_primary": bool(value.get("is_primary", True)),
    }


def _normalize_images(
    value: Any,
    primary_image: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    images: list[dict[str, Any]] = []
    if isinstance(value, list):
        for item in value:
            normalized_item = _normalize_primary_image(item)
            if normalized_item is not None:
                images.append(normalized_item)
    if primary_image is not None and not any(
        image.get("original_url") == primary_image.get("original_url")
        and image.get("thumbnail_url") == primary_image.get("thumbnail_url")
        for image in images
    ):
        images.insert(0, primary_image)
    return images


def _coerce_string_dict(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {
        str(key).strip(): str(item).strip()
        for key, item in value.items()
        if str(key).strip() and str(item).strip()
    }


def _normalize_website(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    if "://" not in normalized:
        normalized = f"https://{normalized}"
    parsed = urlparse(normalized)
    if not parsed.scheme or not parsed.netloc:
        return None
    return normalized


def _normalize_phone(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _normalize_string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    normalized_values = []
    for value in values:
        normalized_value = _normalize_token(value)
        if normalized_value:
            normalized_values.append(normalized_value)
    return sorted(set(normalized_values))


def _normalize_token(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower().replace(" ", "_")


def _safe_int(value: Any, fallback: int | None = None) -> int | None:
    if value is None:
        return fallback
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _safe_float(value: Any, fallback: float | None = None) -> float | None:
    if value is None:
        return fallback
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _clamp_score(value: Any, fallback: float) -> float:
    normalized = _safe_float(value, fallback=fallback)
    if normalized is None:
        normalized = fallback
    return round(min(1.0, max(0.0, normalized)), 2)
