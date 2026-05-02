from __future__ import annotations

import argparse
from collections.abc import Iterable

from app.db.session import SessionLocal
from app.models import City
from app.services.data_import import ExternalPOIImportService
from app.services.import_persistence import (
    city_catalog_size,
    get_city_model,
    import_poi_candidates,
    select_high_quality_candidates,
)
from sqlalchemy import select


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import external POI candidates into PostgreSQL for one city or all seeded cities."
    )
    parser.add_argument("--city-id", type=int, default=None, help="Import only one city by id.")
    parser.add_argument("--all", action="store_true", help="Import all cities from the current catalog.")
    parser.add_argument("--radius-meters", type=int, default=25000)
    parser.add_argument("--limit", type=int, default=180, help="Source candidate limit per city.")
    parser.add_argument("--target-count", type=int, default=100, help="Target number of high-quality POI to keep per city.")
    parser.add_argument("--min-quality", type=float, default=0.55)
    parser.add_argument("--min-popularity", type=float, default=0.45)
    parser.add_argument(
        "--skip-wikimedia",
        action="store_true",
        help="Skip Wikipedia/Wikidata/Wikimedia enrichment requests.",
    )
    return parser


def iter_city_ids(*, session, requested_city_id: int | None, import_all: bool) -> Iterable[int]:
    if requested_city_id is not None:
        yield requested_city_id
        return
    if not import_all:
        raise SystemExit("Pass --city-id <id> or --all.")
    for city_id in session.scalars(select(City.id).order_by(City.id.asc())).all():
        yield int(city_id)


def main() -> None:
    args = build_parser().parse_args()
    service = ExternalPOIImportService.from_env()
    if not service.opentripmap_api_key:
        print("[info] OPENTRIPMAP_API_KEY is not set. Import will use Overpass-only data.")

    with SessionLocal() as session:
        for city_id in iter_city_ids(
            session=session,
            requested_city_id=args.city_id,
            import_all=args.all,
        ):
            city = get_city_model(session, city_id)
            if city is None:
                print(f"[skip] city_id={city_id}: city not found in PostgreSQL")
                continue

            print(f"[start] {city.name} (city_id={city.id})")
            candidates = service.load_city_candidates(
                city,
                radius_meters=args.radius_meters,
                limit=args.limit,
            )
            if not args.skip_wikimedia:
                candidates = service.enrich_candidates_with_wikimedia(candidates)

            selected = select_high_quality_candidates(
                candidates,
                target_count=args.target_count,
                min_quality=args.min_quality,
                min_popularity=args.min_popularity,
            )
            result = import_poi_candidates(
                session,
                city_id=city.id,
                candidates=selected,
            )
            total_catalog = city_catalog_size(session, city.id)
            print(
                f"[done] {city.name}: created={result.created}, "
                f"updated={result.updated}, skipped={result.skipped}, total={total_catalog}"
            )


if __name__ == "__main__":
    main()
