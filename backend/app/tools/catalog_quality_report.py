from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models import City, POI


def build_report() -> dict[str, object]:
    with SessionLocal() as session:
        cities = session.scalars(select(City).order_by(City.id.asc())).all()
        per_city: list[dict[str, object]] = []

        for city in cities:
            pois = session.scalars(
                select(POI)
                .where(POI.city_id == city.id)
                .options(selectinload(POI.images), selectinload(POI.source_links))
            ).all()
            quality_055 = [poi for poi in pois if poi.data_quality_score >= 0.55]
            quality_070 = [poi for poi in pois if poi.data_quality_score >= 0.70]
            with_images = sum(1 for poi in pois if poi.images)
            with_wikidata = sum(1 for poi in pois if poi.wikidata_id)
            with_website = sum(1 for poi in pois if poi.website)
            with_phone = sum(1 for poi in pois if poi.phone)
            avg_quality = round(
                sum(poi.data_quality_score for poi in pois) / max(len(pois), 1),
                2,
            )
            avg_popularity = round(
                sum(poi.popularity_score for poi in pois) / max(len(pois), 1),
                2,
            )
            per_city.append(
                {
                    "city_id": city.id,
                    "name": city.name,
                    "total_pois": len(pois),
                    "target_gap_to_100": max(0, 100 - len(pois)),
                    "quality_gte_0_55": len(quality_055),
                    "quality_gte_0_70": len(quality_070),
                    "with_images": with_images,
                    "with_wikidata": with_wikidata,
                    "with_website": with_website,
                    "with_phone": with_phone,
                    "avg_quality": avg_quality,
                    "avg_popularity": avg_popularity,
                }
            )

        return {
            "cities_total": len(cities),
            "per_city": per_city,
        }


def main() -> None:
    print(json.dumps(build_report(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
