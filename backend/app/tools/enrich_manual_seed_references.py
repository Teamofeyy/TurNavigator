from __future__ import annotations

import argparse
from urllib.parse import urlencode

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models import POI
from app.services.data_import import (
    build_wikipedia_page_url,
    build_wikidata_entity_url,
    build_wikipedia_summary_url,
    enrich_with_wikimedia_context,
    fetch_json,
)
from app.services.import_persistence import import_poi_candidates


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Enrich manual_seed POI with Wikidata/Wikipedia references and images."
    )
    parser.add_argument("--city-id", type=int, required=True)
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--poi-ids", type=str, default="")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    requested_ids = {
        int(item.strip())
        for item in args.poi_ids.split(",")
        if item.strip()
    }

    with SessionLocal() as session:
        statement = (
            select(POI)
            .where(
                POI.city_id == args.city_id,
                POI.source == "manual_seed",
            )
            .options(selectinload(POI.images), selectinload(POI.source_links))
            .order_by(POI.popularity_score.desc(), POI.name.asc())
            .limit(args.limit)
        )
        pois = session.scalars(statement).all()

        if requested_ids:
            pois = [poi for poi in pois if poi.id in requested_ids]

        enriched_candidates: list[dict] = []
        for poi in pois:
            if poi.primary_image_present:
                continue
            candidate = poi_to_candidate(poi)
            wikidata_match = search_wikidata_id(f"{poi.name} Ростов-на-Дону") or search_wikidata_id(poi.name)
            if not wikidata_match:
                continue
            candidate["wikidata_id"] = wikidata_match
            wikidata_entity = fetch_json(build_wikidata_entity_url(wikidata_match))
            wikipedia_title = extract_ruwiki_title(wikidata_entity)
            wikipedia_summary = None
            if wikipedia_title:
                candidate["wikipedia_title"] = wikipedia_title
                candidate["wikipedia_url"] = build_wikipedia_page_url(wikipedia_title)
                wikipedia_summary = fetch_json(build_wikipedia_summary_url(wikipedia_title))
            enriched_candidates.append(
                enrich_with_wikimedia_context(
                    candidate,
                    wikidata_entity=wikidata_entity if isinstance(wikidata_entity, dict) else None,
                    wikipedia_summary=wikipedia_summary if isinstance(wikipedia_summary, dict) else None,
                )
            )

        if not enriched_candidates:
            print(f"[done] city_id={args.city_id}: enriched=0")
            return

        result = import_poi_candidates(
            session,
            city_id=args.city_id,
            candidates=enriched_candidates,
        )
        print(
            f"[done] city_id={args.city_id}: created={result.created}, "
            f"updated={result.updated}, skipped={result.skipped}, enriched={len(enriched_candidates)}"
        )


def search_wikidata_id(search_query: str) -> str | None:
    query = urlencode(
        {
            "action": "wbsearchentities",
            "search": search_query,
            "language": "ru",
            "format": "json",
            "limit": 3,
        }
    )
    payload = fetch_json(
        f"https://www.wikidata.org/w/api.php?{query}"
    )
    results = payload.get("search", []) if isinstance(payload, dict) else []
    for item in results:
        wikidata_id = item.get("id")
        if isinstance(wikidata_id, str) and wikidata_id.startswith("Q"):
            return wikidata_id
    return None


def extract_ruwiki_title(wikidata_entity: dict) -> str | None:
    entities = wikidata_entity.get("entities")
    if not isinstance(entities, dict) or not entities:
        return None
    entity = next(iter(entities.values()))
    sitelinks = entity.get("sitelinks", {}) if isinstance(entity, dict) else {}
    ruwiki = sitelinks.get("ruwiki", {}) if isinstance(sitelinks, dict) else {}
    title = ruwiki.get("title") if isinstance(ruwiki, dict) else None
    return title if isinstance(title, str) and title.strip() else None


def poi_to_candidate(poi: POI) -> dict:
    return {
        "id": poi.id,
        "city_id": poi.city_id,
        "name": poi.name,
        "category": poi.category,
        "subcategory": poi.subcategory,
        "latitude": poi.latitude,
        "longitude": poi.longitude,
        "address": poi.address,
        "description": poi.description,
        "opening_hours": poi.opening_hours,
        "website": poi.website,
        "phone": poi.phone,
        "source": poi.source,
        "external_id": poi.external_id,
        "wikidata_id": poi.wikidata_id,
        "wikipedia_title": poi.wikipedia_title,
        "wikipedia_url": poi.wikipedia_url,
        "wikimedia_commons": poi.wikimedia_commons,
        "osm_tags": poi.osm_tags,
        "estimated_price_level": poi.estimated_price_level,
        "average_cost_rub": poi.average_cost_rub,
        "estimated_visit_minutes": poi.estimated_visit_minutes,
        "popularity_score": poi.popularity_score,
        "data_quality_score": poi.data_quality_score,
        "interests": poi.interests,
        "interest_source": poi.interest_source,
        "primary_image": next(
            (
                {
                    "provider": image.provider,
                    "original_url": image.original_url,
                    "thumbnail_url": image.thumbnail_url,
                    "source_page_url": image.source_page_url,
                    "license": image.license,
                    "author": image.author,
                    "attribution_text": image.attribution_text,
                    "width": image.width,
                    "height": image.height,
                    "is_primary": image.is_primary,
                }
                for image in poi.images
                if image.is_primary
            ),
            None,
        ),
        "images": [
            {
                "provider": image.provider,
                "original_url": image.original_url,
                "thumbnail_url": image.thumbnail_url,
                "source_page_url": image.source_page_url,
                "license": image.license,
                "author": image.author,
                "attribution_text": image.attribution_text,
                "width": image.width,
                "height": image.height,
                "is_primary": image.is_primary,
            }
            for image in poi.images
        ],
        "source_links": [
            {
                "provider": link.provider,
                "external_id": link.external_id,
                "url": link.url,
                "license": link.license,
                "last_synced_at": link.last_synced_at.isoformat() if link.last_synced_at else None,
            }
            for link in poi.source_links
        ],
        "data_freshness_days": poi.data_freshness_days,
        "last_enriched_at": poi.last_enriched_at.isoformat() if poi.last_enriched_at else None,
    }


POI.primary_image_present = property(lambda self: any(image.is_primary for image in self.images))


if __name__ == "__main__":
    main()
