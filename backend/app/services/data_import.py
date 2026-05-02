from __future__ import annotations

import json
import os
import ssl
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote, unquote, urlencode, urlparse
from urllib.request import Request, urlopen

import certifi

from app.core.env import load_env_files
from app.schemas.city import CityBase
from app.services.media_urls import normalize_poi_image_url
from app.services.poi_enrichment import (
    compute_data_quality_score,
    enrich_seed_poi_record,
    estimate_popularity_score,
)

DEFAULT_IMPORT_RADIUS_METERS = 25_000
DEFAULT_OPENTRIPMAP_LIMIT = 120
DEFAULT_HTTP_TIMEOUT_SECONDS = 20
OPENTRIPMAP_DETAIL_TIMEOUT_SECONDS = 8
WIKIMEDIA_TIMEOUT_SECONDS = 8
MAX_OPENTRIPMAP_DETAIL_REQUESTS = 120

OPENTRIPMAP_KIND_CATEGORY_RULES: list[tuple[set[str], tuple[str, str]]] = [
    ({"museums", "cultural", "art_galleries"}, ("culture", "museum")),
    ({"historic", "monuments_and_memorials", "fortifications"}, ("history", "landmark")),
    ({"architecture"}, ("architecture", "landmark")),
    ({"theatres_and_entertainments", "theatres"}, ("entertainment", "theatre")),
    ({"gardens_and_parks", "natural", "nature_reserves"}, ("nature", "park")),
    ({"view_points"}, ("nature", "viewpoint")),
    ({"foods"}, ("food", "restaurant")),
    ({"nightlife"}, ("nightlife", "nightclub")),
    ({"markets"}, ("food", "market")),
    ({"shops"}, ("shopping", "shop")),
    ({"accomodations", "other_hotels"}, ("accommodation", "hotel")),
]

OVERPASS_CATEGORY_RULES: dict[tuple[str, str], tuple[str, str]] = {
    ("tourism", "museum"): ("culture", "museum"),
    ("tourism", "attraction"): ("history", "landmark"),
    ("tourism", "viewpoint"): ("nature", "viewpoint"),
    ("tourism", "hotel"): ("accommodation", "hotel"),
    ("tourism", "hostel"): ("accommodation", "hostel"),
    ("tourism", "guest_house"): ("accommodation", "guest_house"),
    ("historic", "memorial"): ("history", "memorial"),
    ("historic", "monument"): ("history", "monument"),
    ("historic", "castle"): ("history", "castle"),
    ("amenity", "theatre"): ("entertainment", "theatre"),
    ("amenity", "arts_centre"): ("culture", "arts_centre"),
    ("amenity", "cafe"): ("food", "cafe"),
    ("amenity", "restaurant"): ("food", "restaurant"),
    ("amenity", "fast_food"): ("food", "fast_food"),
    ("amenity", "food_court"): ("food", "food_court"),
    ("amenity", "ice_cream"): ("food", "dessert"),
    ("amenity", "bar"): ("nightlife", "bar"),
    ("amenity", "pub"): ("nightlife", "pub"),
    ("amenity", "biergarten"): ("nightlife", "biergarten"),
    ("amenity", "nightclub"): ("nightlife", "nightclub"),
    ("amenity", "marketplace"): ("food", "market"),
    ("leisure", "park"): ("nature", "park"),
    ("leisure", "garden"): ("nature", "garden"),
    ("shop", "mall"): ("shopping", "mall"),
    ("shop", "marketplace"): ("food", "market"),
    ("shop", "department_store"): ("shopping", "department_store"),
    ("shop", "gift"): ("shopping", "gift_shop"),
    ("shop", "souvenir"): ("shopping", "souvenir_shop"),
    ("shop", "clothes"): ("shopping", "clothes_store"),
    ("shop", "shoes"): ("shopping", "shoes_store"),
    ("shop", "sports"): ("shopping", "sports_store"),
    ("shop", "jewelry"): ("shopping", "jewelry_store"),
    ("shop", "cosmetics"): ("shopping", "cosmetics_store"),
    ("shop", "electronics"): ("shopping", "electronics_store"),
    ("shop", "mobile_phone"): ("shopping", "mobile_phone_store"),
    ("shop", "bag"): ("shopping", "bags_store"),
    ("shop", "optician"): ("shopping", "optician"),
    ("shop", "books"): ("shopping", "bookstore"),
    ("shop", "supermarket"): ("food", "supermarket"),
    ("shop", "convenience"): ("food", "convenience_store"),
    ("shop", "bakery"): ("food", "bakery"),
    ("shop", "confectionery"): ("food", "confectionery"),
}

OVERPASS_FILTERS = {
    "tourism": ["museum", "attraction", "viewpoint", "hotel", "hostel", "guest_house"],
    "amenity": [
        "theatre",
        "arts_centre",
        "cafe",
        "restaurant",
        "fast_food",
        "food_court",
        "ice_cream",
        "bar",
        "pub",
        "biergarten",
        "nightclub",
        "marketplace",
    ],
    "historic": ["memorial", "monument", "castle"],
    "leisure": ["park", "garden"],
    "shop": [
        "mall",
        "department_store",
        "gift",
        "souvenir",
        "clothes",
        "shoes",
        "sports",
        "jewelry",
        "cosmetics",
        "electronics",
        "mobile_phone",
        "bag",
        "optician",
        "books",
        "supermarket",
        "convenience",
        "bakery",
        "confectionery",
    ],
}


@dataclass(slots=True, frozen=True)
class ImportCandidate:
    provider: str
    external_id: str
    payload: dict[str, Any]


@dataclass(slots=True)
class ExternalPOIImportService:
    opentripmap_api_key: str | None = None
    opentripmap_language: str = "ru"
    overpass_endpoint: str = "https://overpass-api.de/api/interpreter"

    @classmethod
    def from_env(cls) -> "ExternalPOIImportService":
        load_env_files()
        return cls(
            opentripmap_api_key=os.getenv("OPENTRIPMAP_API_KEY"),
            opentripmap_language=os.getenv("WIKIPEDIA_LANGUAGE", "ru"),
            overpass_endpoint=os.getenv(
                "OVERPASS_ENDPOINT",
                "https://overpass-api.de/api/interpreter",
            ),
        )

    def plan_city_import(
        self,
        city: CityBase,
        *,
        radius_meters: int = DEFAULT_IMPORT_RADIUS_METERS,
        limit: int = DEFAULT_OPENTRIPMAP_LIMIT,
    ) -> dict[str, Any]:
        return {
            "city_id": city.id,
            "city_name": city.name,
            "radius_meters": radius_meters,
            "opentripmap_places_url": (
                build_opentripmap_places_url(
                    city,
                    api_key=self.opentripmap_api_key or "{api_key}",
                    radius_meters=radius_meters,
                    limit=limit,
                )
                if self.opentripmap_api_key
                else None
            ),
            "overpass_query": build_overpass_query(
                city,
                radius_meters=radius_meters,
            ),
            "overpass_endpoint": self.overpass_endpoint,
        }

    def load_city_candidates(
        self,
        city: CityBase,
        *,
        radius_meters: int = DEFAULT_IMPORT_RADIUS_METERS,
        limit: int = DEFAULT_OPENTRIPMAP_LIMIT,
    ) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []

        if self.opentripmap_api_key:
            detail_requests_used = 0
            otm_queries: list[tuple[str | None, int]] = [
                ("foods", max(80, min(limit, 140))),
                ("shops", max(80, min(limit, 140))),
                (None, limit),
            ]
            for kinds, query_limit in otm_queries:
                otm_places_url = build_opentripmap_places_url(
                    city,
                    api_key=self.opentripmap_api_key,
                    radius_meters=radius_meters,
                    limit=query_limit,
                    kinds=kinds,
                )
                try:
                    otm_places_payload = fetch_json(
                        otm_places_url,
                        timeout_seconds=DEFAULT_HTTP_TIMEOUT_SECONDS,
                    )
                except Exception:
                    continue
                if not isinstance(otm_places_payload, list):
                    continue
                for summary in otm_places_payload:
                    if not isinstance(summary, dict):
                        continue
                    xid = str(summary.get("xid") or "").strip()
                    details = None
                    if xid and detail_requests_used < MAX_OPENTRIPMAP_DETAIL_REQUESTS:
                        try:
                            details = fetch_json(
                                build_opentripmap_detail_url(
                                    xid=xid,
                                    api_key=self.opentripmap_api_key,
                                ),
                                timeout_seconds=OPENTRIPMAP_DETAIL_TIMEOUT_SECONDS,
                            )
                            detail_requests_used += 1
                        except Exception:
                            details = None
                    normalized = normalize_opentripmap_place(
                        city=city,
                        place_summary=summary,
                        place_details=details if isinstance(details, dict) else None,
                    )
                    if normalized is not None:
                        candidates.append(normalized)

        overpass_payload = fetch_json(
            self.overpass_endpoint,
            method="POST",
            data=build_overpass_query(city, radius_meters=radius_meters),
            headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
            timeout_seconds=DEFAULT_HTTP_TIMEOUT_SECONDS,
        )
        for element in overpass_payload.get("elements", []) if isinstance(overpass_payload, dict) else []:
            if not isinstance(element, dict):
                continue
            normalized = normalize_overpass_element(city=city, element=element)
            if normalized is not None:
                candidates.append(normalized)

        return deduplicate_and_merge_candidates(candidates)

    def enrich_candidates_with_wikimedia(
        self,
        candidates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        enriched_candidates: list[dict[str, Any]] = []
        for candidate in candidates:
            wikidata_id = candidate.get("wikidata_id")
            wikipedia_title = candidate.get("wikipedia_title")

            wikidata_entity = None
            if wikidata_id:
                try:
                    wikidata_entity = fetch_json(
                        build_wikidata_entity_url(wikidata_id),
                        timeout_seconds=WIKIMEDIA_TIMEOUT_SECONDS,
                    )
                except Exception:
                    wikidata_entity = None

            wikipedia_summary = None
            if wikipedia_title:
                try:
                    wikipedia_summary = fetch_json(
                        build_wikipedia_summary_url(
                            wikipedia_title,
                            language=self.opentripmap_language,
                        ),
                        timeout_seconds=WIKIMEDIA_TIMEOUT_SECONDS,
                    )
                except Exception:
                    wikipedia_summary = None

            enriched_candidates.append(
                enrich_with_wikimedia_context(
                    candidate,
                    wikidata_entity=wikidata_entity if isinstance(wikidata_entity, dict) else None,
                    wikipedia_summary=wikipedia_summary if isinstance(wikipedia_summary, dict) else None,
                )
            )
        return deduplicate_and_merge_candidates(enriched_candidates)


def build_opentripmap_places_url(
    city: CityBase,
    *,
    api_key: str,
    radius_meters: int = DEFAULT_IMPORT_RADIUS_METERS,
    limit: int = DEFAULT_OPENTRIPMAP_LIMIT,
    kinds: str | None = None,
) -> str:
    query_params = {
        "radius": radius_meters,
        "lon": city.longitude,
        "lat": city.latitude,
        "limit": limit,
        "format": "json",
        "apikey": api_key,
    }
    if kinds:
        query_params["kinds"] = kinds
    return f"https://api.opentripmap.com/0.1/ru/places/radius?{urlencode(query_params)}"


def build_opentripmap_detail_url(*, xid: str, api_key: str) -> str:
    safe_xid = quote(xid, safe="")
    return f"https://api.opentripmap.com/0.1/ru/places/xid/{safe_xid}?apikey={quote(api_key, safe='')}"


def build_wikidata_entity_url(wikidata_id: str) -> str:
    safe_wikidata_id = quote(wikidata_id, safe="")
    return f"https://www.wikidata.org/wiki/Special:EntityData/{safe_wikidata_id}.json"


def build_wikipedia_summary_url(title: str, *, language: str = "ru") -> str:
    safe_title = quote(title.replace(" ", "_"), safe=":_-()")
    return (
        f"https://{language}.wikipedia.org/api/rest_v1/page/summary/"
        f"{safe_title}"
    )


def build_wikipedia_page_url(title: str, *, language: str = "ru") -> str:
    safe_title = quote(title.replace(" ", "_"), safe=":_-()")
    return f"https://{language}.wikipedia.org/wiki/{safe_title}"


def build_overpass_query(
    city: CityBase,
    *,
    radius_meters: int = DEFAULT_IMPORT_RADIUS_METERS,
) -> str:
    query_parts: list[str] = []
    for key, values in OVERPASS_FILTERS.items():
        for value in values:
            query_parts.append(
                f'node["{key}"="{value}"](around:{radius_meters},{city.latitude},{city.longitude});'
            )
            query_parts.append(
                f'way["{key}"="{value}"](around:{radius_meters},{city.latitude},{city.longitude});'
            )
            query_parts.append(
                f'relation["{key}"="{value}"](around:{radius_meters},{city.latitude},{city.longitude});'
            )

    body = "".join(query_parts)
    return f"[out:json][timeout:45];({body});out center tags;"


def fetch_json(
    url: str,
    *,
    method: str = "GET",
    data: str | None = None,
    headers: dict[str, str] | None = None,
    timeout_seconds: int = DEFAULT_HTTP_TIMEOUT_SECONDS,
) -> Any:
    encoded_data = data.encode("utf-8") if data is not None else None
    request_headers = {
        "Accept": "application/json",
        "User-Agent": "TravelContextPrototype/0.1",
    }
    if headers:
        request_headers.update(headers)
    request = Request(
        url,
        data=encoded_data,
        headers=request_headers,
        method=method.upper(),
    )
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    with urlopen(request, timeout=timeout_seconds, context=ssl_context) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_opentripmap_place(
    *,
    city: CityBase,
    place_summary: dict[str, Any],
    place_details: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    xid = str(place_summary.get("xid") or place_details and place_details.get("xid") or "").strip()
    name = str(place_summary.get("name") or place_details and place_details.get("name") or "").strip()
    point = place_summary.get("point") or place_details and place_details.get("point") or {}
    latitude = _safe_float(point.get("lat"))
    longitude = _safe_float(point.get("lon"))
    if not xid or not name or latitude is None or longitude is None:
        return None

    details = place_details or {}
    kinds = _parse_opentripmap_kinds(place_summary.get("kinds") or details.get("kinds"))
    category, subcategory = _map_opentripmap_category(kinds)
    wikidata_id = _extract_wikidata_id(details.get("wikidata") or place_summary.get("wikidata"))
    wikipedia_title = _normalize_wikipedia_title(details.get("wikipedia"))
    wikipedia_url = (
        build_wikipedia_page_url(wikipedia_title)
        if wikipedia_title
        else None
    )

    raw_description = (
        _dig(details, "wikipedia_extracts", "text")
        or _dig(details, "info", "descr")
        or details.get("description")
    )
    primary_image = _build_opentripmap_primary_image(details)
    record: dict[str, Any] = {
        "id": 0,
        "city_id": city.id,
        "name": name,
        "category": category,
        "subcategory": subcategory,
        "latitude": latitude,
        "longitude": longitude,
        "address": _join_address(details.get("address")),
        "description": raw_description,
        "opening_hours": None,
        "website": _normalize_url(_dig(details, "otm", "url")),
        "phone": None,
        "source": "opentripmap",
        "external_id": xid,
        "wikidata_id": wikidata_id,
        "wikipedia_title": wikipedia_title,
        "wikipedia_url": wikipedia_url,
        "wikimedia_commons": None,
        "osm_tags": _tags_from_otm_kinds(kinds),
        "estimated_price_level": "unknown",
        "average_cost_rub": 0,
        "estimated_visit_minutes": _estimate_visit_minutes(category, subcategory),
        "source_rating": _safe_int(details.get("rate") or place_summary.get("rate")),
        "primary_image": primary_image,
        "images": [primary_image] if primary_image else [],
        "source_links": [
            {
                "provider": "opentripmap",
                "external_id": xid,
                "url": build_opentripmap_detail_url(xid=xid, api_key="{api_key}"),
                "license": "ODbL / CC BY-SA via OpenTripMap data bundle",
                "last_synced_at": datetime.now(UTC).isoformat(),
            }
        ],
        "data_freshness_days": 0,
        "last_enriched_at": datetime.now(UTC).isoformat(),
    }
    record["popularity_score"] = estimate_popularity_score(record)
    record["data_quality_score"] = compute_data_quality_score(record)
    return enrich_seed_poi_record(record)


def normalize_overpass_element(
    *,
    city: CityBase,
    element: dict[str, Any],
) -> dict[str, Any] | None:
    tags = _string_dict(element.get("tags"))
    name = str(tags.get("name") or "").strip()
    if not name:
        return None
    latitude = _safe_float(element.get("lat") or _dig(element, "center", "lat"))
    longitude = _safe_float(element.get("lon") or _dig(element, "center", "lon"))
    if latitude is None or longitude is None:
        return None

    category, subcategory = _map_overpass_category(tags)
    provider_kind = element.get("type") or "element"
    external_id = f"{provider_kind}/{element.get('id')}"
    wikipedia_title = _normalize_wikipedia_title(tags.get("wikipedia"))
    wikipedia_url = (
        build_wikipedia_page_url(wikipedia_title)
        if wikipedia_title
        else None
    )
    record: dict[str, Any] = {
        "id": 0,
        "city_id": city.id,
        "name": name,
        "category": category,
        "subcategory": subcategory,
        "latitude": latitude,
        "longitude": longitude,
        "address": _overpass_address(tags),
        "description": tags.get("description"),
        "opening_hours": tags.get("opening_hours"),
        "website": _normalize_url(tags.get("website") or tags.get("contact:website")),
        "phone": tags.get("phone") or tags.get("contact:phone"),
        "source": "overpass",
        "external_id": external_id,
        "wikidata_id": _extract_wikidata_id(tags.get("wikidata")),
        "wikipedia_title": wikipedia_title,
        "wikipedia_url": wikipedia_url,
        "wikimedia_commons": tags.get("wikimedia_commons"),
        "osm_tags": tags,
        "estimated_price_level": _infer_price_level(tags),
        "average_cost_rub": 0,
        "estimated_visit_minutes": _estimate_visit_minutes(category, subcategory),
        "primary_image": _build_osm_image(tags),
        "images": [],
        "source_links": [
            {
                "provider": "overpass",
                "external_id": external_id,
                "url": f"https://www.openstreetmap.org/{external_id}",
                "license": "ODbL",
                "last_synced_at": datetime.now(UTC).isoformat(),
            }
        ],
        "data_freshness_days": 0,
        "last_enriched_at": datetime.now(UTC).isoformat(),
    }
    record["popularity_score"] = estimate_popularity_score(record)
    record["data_quality_score"] = compute_data_quality_score(record)
    return enrich_seed_poi_record(record)


def enrich_with_wikimedia_context(
    poi_record: dict[str, Any],
    *,
    wikidata_entity: dict[str, Any] | None = None,
    wikipedia_summary: dict[str, Any] | None = None,
    commons_media: dict[str, Any] | None = None,
) -> dict[str, Any]:
    enriched_record = dict(poi_record)
    wikipedia_title = enriched_record.get("wikipedia_title")

    if wikidata_entity:
        claims = _dig(wikidata_entity, "entities")
        first_entity = next(iter(claims.values()), {}) if isinstance(claims, dict) else {}
        commons_name = _extract_commons_name(first_entity)
        if commons_name and not enriched_record.get("wikimedia_commons"):
            enriched_record["wikimedia_commons"] = commons_name
        if not enriched_record.get("description"):
            enriched_record["description"] = _extract_wikidata_description(first_entity)

    if wikipedia_summary:
        if not wikipedia_title:
            wikipedia_title = wikipedia_summary.get("title")
            enriched_record["wikipedia_title"] = wikipedia_title
        if not enriched_record.get("wikipedia_url") and wikipedia_title:
            enriched_record["wikipedia_url"] = build_wikipedia_page_url(wikipedia_title)
        if not enriched_record.get("description"):
            enriched_record["description"] = wikipedia_summary.get("extract")
        if not enriched_record.get("primary_image"):
            page_thumbnail = wikipedia_summary.get("thumbnail") or {}
            page_thumbnail_url = normalize_poi_image_url(_normalize_url(page_thumbnail.get("source")))
            image = {
                "provider": "wikipedia",
                "original_url": page_thumbnail_url,
                "thumbnail_url": page_thumbnail_url,
                "source_page_url": _normalize_url(wikipedia_summary.get("content_urls", {}).get("desktop", {}).get("page")),
                "license": "CC BY-SA",
                "author": None,
                "attribution_text": None,
                "width": _safe_int(page_thumbnail.get("width")),
                "height": _safe_int(page_thumbnail.get("height")),
                "is_primary": True,
            }
            if image["original_url"]:
                enriched_record["primary_image"] = image

    if commons_media:
        original_url = normalize_poi_image_url(_normalize_url(
            commons_media.get("original")
            or _dig(commons_media, "preferred", "url")
        ))
        thumbnail_url = normalize_poi_image_url(_normalize_url(
            commons_media.get("thumbnail")
            or _dig(commons_media, "thumbnail", "url")
        ))
        if original_url or thumbnail_url:
            enriched_record["primary_image"] = {
                "provider": "wikimedia",
                "original_url": original_url,
                "thumbnail_url": thumbnail_url,
                "source_page_url": _normalize_url(commons_media.get("descriptionurl")),
                "license": commons_media.get("license", "CC BY-SA"),
                "author": commons_media.get("artist"),
                "attribution_text": commons_media.get("attribution"),
                "width": _safe_int(commons_media.get("width")),
                "height": _safe_int(commons_media.get("height")),
                "is_primary": True,
            }

    enriched_record["data_quality_score"] = compute_data_quality_score(enriched_record)
    enriched_record["popularity_score"] = estimate_popularity_score(enriched_record)
    return enrich_seed_poi_record(enriched_record)


def deduplicate_and_merge_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged_by_key: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        if not candidate:
            continue
        key = _candidate_merge_key(candidate)
        if key not in merged_by_key:
            merged_by_key[key] = dict(candidate)
            continue
        merged_by_key[key] = merge_poi_records(merged_by_key[key], candidate)
    return list(merged_by_key.values())


def merge_poi_records(primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    merged = dict(primary)
    for field_name in [
        "name",
        "address",
        "opening_hours",
        "website",
        "phone",
        "wikidata_id",
        "wikipedia_title",
        "wikipedia_url",
        "wikimedia_commons",
        "primary_image",
    ]:
        merged[field_name] = _prefer_richer_value(primary.get(field_name), secondary.get(field_name))

    merged["description"] = _prefer_longer_text(
        primary.get("description"),
        secondary.get("description"),
    )
    merged["category"], merged["subcategory"] = _prefer_category_pair(primary, secondary)
    merged["osm_tags"] = _merged_dict(primary.get("osm_tags"), secondary.get("osm_tags"))
    merged["images"] = _merge_images(primary.get("images"), secondary.get("images"), merged.get("primary_image"))
    merged["source_links"] = _merge_source_links(primary.get("source_links"), secondary.get("source_links"))
    merged["interests"] = sorted(
        set(_string_list(primary.get("interests"))) | set(_string_list(secondary.get("interests")))
    )

    average_cost = max(
        _safe_int(primary.get("average_cost_rub"), fallback=0) or 0,
        _safe_int(secondary.get("average_cost_rub"), fallback=0) or 0,
    )
    merged["average_cost_rub"] = average_cost
    merged["estimated_visit_minutes"] = max(
        _safe_int(primary.get("estimated_visit_minutes"), fallback=60) or 60,
        _safe_int(secondary.get("estimated_visit_minutes"), fallback=60) or 60,
    )
    merged["estimated_price_level"] = _prefer_richer_value(
        primary.get("estimated_price_level"),
        secondary.get("estimated_price_level"),
    ) or "unknown"
    merged["popularity_score"] = round(
        max(
            _safe_float(primary.get("popularity_score"), fallback=0.0) or 0.0,
            _safe_float(secondary.get("popularity_score"), fallback=0.0) or 0.0,
        ),
        2,
    )
    merged["data_quality_score"] = round(
        max(
            _safe_float(primary.get("data_quality_score"), fallback=0.0) or 0.0,
            _safe_float(secondary.get("data_quality_score"), fallback=0.0) or 0.0,
        ),
        2,
    )
    merged["source"] = "merged_external"
    merged["external_id"] = _prefer_richer_value(primary.get("external_id"), secondary.get("external_id")) or "merged"
    merged["data_freshness_days"] = min(
        _safe_int(primary.get("data_freshness_days"), fallback=0) or 0,
        _safe_int(secondary.get("data_freshness_days"), fallback=0) or 0,
    )
    merged["last_enriched_at"] = datetime.now(UTC).isoformat()
    return enrich_seed_poi_record(merged)


def _parse_opentripmap_kinds(value: Any) -> set[str]:
    if isinstance(value, str):
        return {
            item.strip().lower()
            for item in value.split(",")
            if item.strip()
        }
    if isinstance(value, list):
        return {
            str(item).strip().lower()
            for item in value
            if str(item).strip()
        }
    return set()


def _map_opentripmap_category(kinds: set[str]) -> tuple[str, str]:
    for tokens, mapping in OPENTRIPMAP_KIND_CATEGORY_RULES:
        if kinds.intersection(tokens):
            return mapping
    return ("history", "landmark")


def _tags_from_otm_kinds(kinds: set[str]) -> dict[str, str]:
    if "museums" in kinds:
        return {"tourism": "museum"}
    if "view_points" in kinds:
        return {"tourism": "viewpoint"}
    if "gardens_and_parks" in kinds:
        return {"leisure": "park"}
    if "theatres_and_entertainments" in kinds:
        return {"amenity": "theatre"}
    if "foods" in kinds:
        return {"amenity": "restaurant"}
    if "markets" in kinds:
        return {"amenity": "marketplace"}
    if "shops" in kinds:
        return {"shop": "yes"}
    return {"tourism": "attraction"}


def _map_overpass_category(tags: dict[str, str]) -> tuple[str, str]:
    for key, value in tags.items():
        mapping = OVERPASS_CATEGORY_RULES.get((key, value))
        if mapping:
            return mapping
    return ("history", "landmark")


def _infer_price_level(tags: dict[str, str]) -> str:
    stars = _safe_int(tags.get("stars"))
    if stars is not None:
        if stars >= 4:
            return "premium"
        if stars == 3:
            return "medium"
    if "cafe" in tags.values() or "fast_food" in tags.values():
        return "budget"
    if "restaurant" in tags.values():
        return "medium"
    return "unknown"


def _estimate_visit_minutes(category: str, subcategory: str) -> int:
    if category in {"culture", "history"}:
        return 90
    if category == "food":
        return 60
    if category == "nature":
        return 75
    if category == "shopping" and subcategory == "mall":
        return 120
    if category == "shopping":
        return 45
    if subcategory in {"hotel", "hostel", "guest_house"}:
        return 30
    return 60


def _build_opentripmap_primary_image(details: dict[str, Any]) -> dict[str, Any] | None:
    preview = details.get("preview") or {}
    image_url = normalize_poi_image_url(
        _normalize_url(preview.get("source") or details.get("image"))
    )
    if not image_url:
        return None
    return {
        "provider": "opentripmap",
        "original_url": image_url,
        "thumbnail_url": image_url,
        "source_page_url": _normalize_url(_dig(details, "otm", "url")),
        "license": None,
        "author": None,
        "attribution_text": None,
        "width": _safe_int(preview.get("width")),
        "height": _safe_int(preview.get("height")),
        "is_primary": True,
    }


def _build_osm_image(tags: dict[str, str]) -> dict[str, Any] | None:
    image_url = normalize_poi_image_url(_normalize_url(tags.get("image")))
    if not image_url:
        return None
    return {
        "provider": "osm",
        "original_url": image_url,
        "thumbnail_url": image_url,
        "source_page_url": image_url,
        "license": None,
        "author": None,
        "attribution_text": None,
        "width": None,
        "height": None,
        "is_primary": True,
    }


def _extract_wikidata_id(value: Any) -> str | None:
    normalized = str(value or "").strip()
    if normalized.startswith("Q"):
        return normalized
    return None


def _normalize_wikipedia_title(value: Any) -> str | None:
    normalized = str(value or "").strip()
    if not normalized:
        return None
    if normalized.startswith("//"):
        normalized = f"https:{normalized}"
    if normalized.startswith("http://") or normalized.startswith("https://"):
        parsed = urlparse(normalized)
        if "/wiki/" in parsed.path:
            normalized = parsed.path.split("/wiki/", 1)[1]
        else:
            normalized = parsed.path.rsplit("/", 1)[-1]
    normalized = unquote(normalized)
    if ":" in normalized:
        _, normalized = normalized.split(":", 1)
    normalized = normalized.replace("_", " ").strip()
    return normalized or None


def _extract_commons_name(entity: dict[str, Any]) -> str | None:
    statements = _dig(entity, "claims", "P373")
    if not isinstance(statements, list) or not statements:
        return None
    value = _dig(statements[0], "mainsnak", "datavalue", "value")
    if not value:
        return None
    return f"Category:{value}"


def _extract_wikidata_description(entity: dict[str, Any]) -> str | None:
    descriptions = entity.get("descriptions") or {}
    for language in ["ru", "en"]:
        value = descriptions.get(language) or {}
        text = value.get("value")
        if text:
            return str(text).strip()
    return None


def _candidate_merge_key(candidate: dict[str, Any]) -> str:
    wikidata_id = candidate.get("wikidata_id")
    if wikidata_id:
        return f"wikidata:{wikidata_id}"
    source = str(candidate.get("source") or "").strip()
    external_id = str(candidate.get("external_id") or "").strip()
    if source and external_id:
        return f"{source}:{external_id}"
    latitude = candidate.get("latitude")
    longitude = candidate.get("longitude")
    name = str(candidate.get("name") or "").strip().lower()
    return f"{name}:{latitude}:{longitude}"


def _prefer_category_pair(
    primary: dict[str, Any],
    secondary: dict[str, Any],
) -> tuple[str, str]:
    primary_pair = (primary.get("category"), primary.get("subcategory"))
    secondary_pair = (secondary.get("category"), secondary.get("subcategory"))
    if primary_pair[0] == "history" and primary_pair[1] == "landmark" and secondary_pair[0]:
        return secondary_pair
    return (
        _prefer_richer_value(primary_pair[0], secondary_pair[0]) or "history",
        _prefer_richer_value(primary_pair[1], secondary_pair[1]) or "landmark",
    )


def _prefer_richer_value(primary: Any, secondary: Any) -> Any:
    if not primary and secondary:
        return secondary
    if primary and not secondary:
        return primary
    if isinstance(primary, str) and isinstance(secondary, str):
        return secondary if len(secondary) > len(primary) else primary
    return primary or secondary


def _prefer_longer_text(primary: Any, secondary: Any) -> str | None:
    primary_text = str(primary).strip() if primary else ""
    secondary_text = str(secondary).strip() if secondary else ""
    if len(secondary_text) > len(primary_text):
        return secondary_text or None
    return primary_text or None


def _merge_images(primary: Any, secondary: Any, primary_image: Any) -> list[dict[str, Any]]:
    images: list[dict[str, Any]] = []
    seen_keys: set[tuple[str | None, str | None]] = set()
    for collection in [primary, secondary]:
        if not isinstance(collection, list):
            continue
        for image in collection:
            if not isinstance(image, dict):
                continue
            key = (image.get("original_url"), image.get("thumbnail_url"))
            if key in seen_keys:
                continue
            seen_keys.add(key)
            images.append(dict(image))
    if isinstance(primary_image, dict):
        key = (primary_image.get("original_url"), primary_image.get("thumbnail_url"))
        if key not in seen_keys:
            images.insert(0, dict(primary_image))
    return images


def _merge_source_links(primary: Any, secondary: Any) -> list[dict[str, Any]]:
    merged_links: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()
    for collection in [primary, secondary]:
        if not isinstance(collection, list):
            continue
        for item in collection:
            if not isinstance(item, dict):
                continue
            provider = str(item.get("provider") or "").strip().lower()
            external_id = str(item.get("external_id") or "").strip()
            if not provider or not external_id:
                continue
            key = (provider, external_id)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            merged_links.append(dict(item))
    return merged_links


def _merged_dict(primary: Any, secondary: Any) -> dict[str, str]:
    result = _string_dict(primary)
    result.update(_string_dict(secondary))
    return result


def _join_address(value: Any) -> str:
    if not isinstance(value, dict):
        return ""
    ordered_keys = [
        "road",
        "pedestrian",
        "house_number",
        "suburb",
        "city",
        "state",
    ]
    parts = [
        str(value.get(key)).strip()
        for key in ordered_keys
        if str(value.get(key) or "").strip()
    ]
    return ", ".join(parts)


def _overpass_address(tags: dict[str, str]) -> str:
    parts = [
        tags.get("addr:street"),
        tags.get("addr:housenumber"),
        tags.get("addr:city"),
    ]
    normalized_parts = [str(part).strip() for part in parts if str(part or "").strip()]
    if normalized_parts:
        return ", ".join(normalized_parts)
    return tags.get("addr:full") or ""


def _string_dict(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    normalized: dict[str, str] = {}
    for key, item in value.items():
        normalized_key = str(key).strip()
        normalized_value = str(item).strip()
        if normalized_key and normalized_value:
            normalized[normalized_key] = normalized_value
    return normalized


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip().lower() for item in value if str(item).strip()]


def _normalize_url(value: Any) -> str | None:
    raw_value = str(value or "").strip()
    if not raw_value:
        return None
    if "://" not in raw_value:
        raw_value = f"https://{raw_value}"
    return raw_value


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


def _dig(payload: Any, *keys: str) -> Any:
    current = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current
