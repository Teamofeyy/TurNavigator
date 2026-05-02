from __future__ import annotations

from dataclasses import dataclass
from math import radians, cos, sin, asin, sqrt
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import City, POI, POIImage, POISourceLink
from app.services.media_urls import normalize_poi_image_url

CATEGORY_MIN_QUALITY: dict[str, float] = {
    "food": 0.35,
    "nightlife": 0.35,
    "shopping": 0.35,
    "entertainment": 0.4,
}

CATEGORY_MIN_POPULARITY: dict[str, float] = {
    "food": 0.2,
    "nightlife": 0.2,
    "shopping": 0.2,
    "entertainment": 0.25,
}

CATEGORY_BASE_QUOTAS: dict[str, int] = {
    "food": 24,
    "nightlife": 10,
    "shopping": 12,
    "entertainment": 10,
}


@dataclass(slots=True)
class ImportResult:
    created: int = 0
    updated: int = 0
    skipped: int = 0


def select_high_quality_candidates(
    candidates: list[dict[str, Any]],
    *,
    target_count: int = 100,
    min_quality: float = 0.55,
    min_popularity: float = 0.45,
) -> list[dict[str, Any]]:
    filtered = [
        candidate
        for candidate in candidates
        if (candidate.get("data_quality_score") or 0)
        >= CATEGORY_MIN_QUALITY.get(str(candidate.get("category") or "").strip().lower(), min_quality)
        and (candidate.get("popularity_score") or 0)
        >= CATEGORY_MIN_POPULARITY.get(str(candidate.get("category") or "").strip().lower(), min_popularity)
    ]
    ranked = sorted(filtered, key=_candidate_sort_key, reverse=True)

    selected: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()

    for category, base_quota in CATEGORY_BASE_QUOTAS.items():
        quota = min(base_quota, max(0, target_count // 4))
        if quota <= 0:
            continue
        category_items = [
            item
            for item in ranked
            if str(item.get("category") or "").strip().lower() == category
        ]
        for item in category_items[:quota]:
            key = (
                str(item.get("source") or "").strip(),
                str(item.get("external_id") or "").strip(),
            )
            if key in seen_keys:
                continue
            seen_keys.add(key)
            selected.append(item)

    for item in ranked:
        if len(selected) >= target_count:
            break
        key = (
            str(item.get("source") or "").strip(),
            str(item.get("external_id") or "").strip(),
        )
        if key in seen_keys:
            continue
        seen_keys.add(key)
        selected.append(item)

    return selected[:target_count]


def import_poi_candidates(
    session: Session,
    *,
    city_id: int,
    candidates: list[dict[str, Any]],
) -> ImportResult:
    result = ImportResult()
    for candidate in candidates:
        existing = _find_existing_poi(session, city_id=city_id, candidate=candidate)
        if existing is None:
            poi = _build_poi_model(city_id=city_id, candidate=candidate)
            session.add(poi)
            session.flush()
            result.created += 1
        else:
            poi = existing
            _apply_candidate_to_poi(poi, candidate)
            poi.images.clear()
            poi.source_links.clear()
            session.flush()
            result.updated += 1

        poi.images.extend(_build_image_models(candidate.get("images") or [], candidate.get("primary_image")))
        poi.source_links.extend(_build_source_link_models(candidate.get("source_links") or []))

    session.commit()
    return result


def city_catalog_size(session: Session, city_id: int) -> int:
    return session.query(POI).filter(POI.city_id == city_id).count()


def get_city_model(session: Session, city_id: int) -> City | None:
    return session.get(City, city_id)


def _find_existing_poi(session: Session, *, city_id: int, candidate: dict[str, Any]) -> POI | None:
    source = str(candidate.get("source") or "").strip()
    external_id = str(candidate.get("external_id") or "").strip()
    if source and external_id:
        by_source = session.execute(
            select(POI)
            .where(POI.city_id == city_id, POI.source == source, POI.external_id == external_id)
            .options(selectinload(POI.images), selectinload(POI.source_links))
        ).scalars().first()
        if by_source is not None:
            return by_source

    wikidata_id = candidate.get("wikidata_id")
    if wikidata_id:
        by_wikidata = session.execute(
            select(POI)
            .where(POI.city_id == city_id, POI.wikidata_id == wikidata_id)
            .options(selectinload(POI.images), selectinload(POI.source_links))
        ).scalars().first()
        if by_wikidata is not None:
            return by_wikidata

    name = str(candidate.get("name") or "").strip()
    latitude = candidate.get("latitude")
    longitude = candidate.get("longitude")
    if name and latitude is not None and longitude is not None:
        name_matches = session.execute(
            select(POI)
            .where(POI.city_id == city_id, POI.name == name)
            .options(selectinload(POI.images), selectinload(POI.source_links))
        ).scalars().all()
        for poi in name_matches:
            if _distance_km(poi.latitude, poi.longitude, float(latitude), float(longitude)) <= 0.15:
                return poi

    return None


def _build_poi_model(*, city_id: int, candidate: dict[str, Any]) -> POI:
    payload = _poi_payload(city_id=city_id, candidate=candidate)
    return POI(**payload)


def _apply_candidate_to_poi(poi: POI, candidate: dict[str, Any]) -> None:
    payload = _poi_payload(city_id=poi.city_id, candidate=candidate)
    for key, value in payload.items():
        setattr(poi, key, value)


def _poi_payload(*, city_id: int, candidate: dict[str, Any]) -> dict[str, Any]:
    payload = dict(candidate)
    for transient_field in [
        "id",
        "images",
        "source_links",
        "primary_image",
        "source_rating",
    ]:
        payload.pop(transient_field, None)
    payload["city_id"] = city_id
    payload["name"] = _truncate_str(payload.get("name"), 255) or "Без названия"
    payload["category"] = _truncate_str(payload.get("category"), 64) or "history"
    payload["subcategory"] = _truncate_str(payload.get("subcategory"), 128) or "landmark"
    payload["opening_hours"] = _truncate_str(payload.get("opening_hours"), 255)
    payload["website"] = _truncate_str(payload.get("website"), 512)
    payload["phone"] = _truncate_str(payload.get("phone"), 128)
    payload["source"] = _truncate_str(payload.get("source"), 64) or "merged_external"
    payload["external_id"] = _truncate_str(payload.get("external_id"), 255) or "external"
    payload["wikidata_id"] = _truncate_str(payload.get("wikidata_id"), 32)
    payload["wikipedia_title"] = _truncate_str(payload.get("wikipedia_title"), 255)
    payload["wikipedia_url"] = _truncate_str(payload.get("wikipedia_url"), 512)
    payload["wikimedia_commons"] = _truncate_str(payload.get("wikimedia_commons"), 255)
    payload["estimated_price_level"] = _truncate_str(payload.get("estimated_price_level"), 32) or "unknown"
    payload["interest_source"] = _truncate_str(payload.get("interest_source"), 32) or "automatic"
    payload["average_cost_rub"] = int(payload.get("average_cost_rub") or 0)
    payload["estimated_visit_minutes"] = int(payload.get("estimated_visit_minutes") or 60)
    payload["data_freshness_days"] = int(payload.get("data_freshness_days") or 0)
    return payload


def _build_image_models(
    images: list[dict[str, Any]],
    primary_image: dict[str, Any] | None,
) -> list[POIImage]:
    normalized_images = list(images)
    if primary_image and not any(
        image.get("original_url") == primary_image.get("original_url")
        and image.get("thumbnail_url") == primary_image.get("thumbnail_url")
        for image in normalized_images
    ):
        normalized_images.insert(0, primary_image)

    models: list[POIImage] = []
    seen_keys: set[tuple[str | None, str | None, str]] = set()
    for image in normalized_images:
        if not isinstance(image, dict):
            continue
        key = (
            image.get("original_url"),
            image.get("thumbnail_url"),
            str(image.get("provider") or "unknown"),
        )
        if key in seen_keys:
            continue
        seen_keys.add(key)
        models.append(
            POIImage(
                provider=image.get("provider") or "unknown",
                original_url=normalize_poi_image_url(image.get("original_url")),
                thumbnail_url=normalize_poi_image_url(image.get("thumbnail_url")),
                source_page_url=image.get("source_page_url"),
                license=image.get("license"),
                author=image.get("author"),
                attribution_text=image.get("attribution_text"),
                width=image.get("width"),
                height=image.get("height"),
                is_primary=bool(image.get("is_primary", False)),
            )
        )
    return models


def _build_source_link_models(source_links: list[dict[str, Any]]) -> list[POISourceLink]:
    models: list[POISourceLink] = []
    seen_keys: set[tuple[str, str]] = set()
    for source_link in source_links:
        if not isinstance(source_link, dict):
            continue
        provider = str(source_link.get("provider") or "").strip()
        external_id = str(source_link.get("external_id") or "").strip()
        if not provider or not external_id:
            continue
        key = (provider, external_id)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        models.append(
            POISourceLink(
                provider=provider,
                external_id=external_id,
                url=source_link.get("url"),
                license=source_link.get("license"),
                last_synced_at=source_link.get("last_synced_at"),
            )
        )
    return models


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    )
    return 2 * earth_radius_km * asin(sqrt(a))


def _candidate_sort_key(item: dict[str, Any]) -> tuple[float, float, int, bool, bool, bool]:
    return (
        item.get("data_quality_score") or 0,
        item.get("popularity_score") or 0,
        len(str(item.get("description") or "")),
        bool(item.get("primary_image")),
        bool(item.get("website")),
        bool(item.get("phone")),
    )


def _truncate_str(value: Any, max_length: int) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    return normalized[:max_length]
