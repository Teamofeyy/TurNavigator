from __future__ import annotations

import argparse

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models import POI
from app.services.website_media_enrichment import (
    WebsiteMediaResult,
    enrich_poi_with_website_media,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Enrich POI catalog with website-derived og:image/twitter:image assets."
    )
    parser.add_argument("--city-id", type=int, required=True, help="City id to enrich.")
    parser.add_argument(
        "--categories",
        type=str,
        default="food,shopping,nightlife,entertainment",
        help="Comma-separated normalized categories to scan.",
    )
    parser.add_argument("--limit", type=int, default=120, help="Maximum number of POI to scan.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    categories = [item.strip().lower() for item in args.categories.split(",") if item.strip()]
    result = WebsiteMediaResult()

    with SessionLocal() as session:
        statement = (
            select(POI)
            .where(
                POI.city_id == args.city_id,
                POI.category.in_(categories),
                POI.website.is_not(None),
            )
            .options(selectinload(POI.images))
            .order_by(POI.popularity_score.desc(), POI.data_quality_score.desc(), POI.name.asc())
            .limit(args.limit)
        )
        pois = session.scalars(statement).all()
        for poi in pois:
            result.scanned += 1
            if poi.images:
                result.skipped += 1
                continue
            try:
                enriched = enrich_poi_with_website_media(poi)
            except Exception:
                result.failed += 1
                continue
            if enriched:
                result.enriched += 1
            else:
                result.skipped += 1

        session.commit()

    print(
        f"[done] city_id={args.city_id}: scanned={result.scanned}, "
        f"enriched={result.enriched}, skipped={result.skipped}, failed={result.failed}"
    )


if __name__ == "__main__":
    main()

