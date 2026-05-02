from __future__ import annotations

from app.db.session import SessionLocal
from app.models import City, POI, POIImage, POISourceLink
from app.services.seed_loader import get_city_records, get_poi_records


def seed_database() -> dict[str, int]:
    created_cities = 0
    updated_cities = 0
    created_pois = 0
    updated_pois = 0

    with SessionLocal() as session:
        for city_record in get_city_records():
            city_payload = city_record.model_dump()
            city = session.get(City, city_record.id)
            if city is None:
                city = City(**city_payload)
                session.add(city)
                created_cities += 1
            else:
                for key, value in city_payload.items():
                    setattr(city, key, value)
                updated_cities += 1

        session.flush()

        for poi_record in get_poi_records():
            poi_payload = poi_record.model_dump(
                exclude={"primary_image", "images", "source_links"}
            )
            poi = session.get(POI, poi_record.id)
            if poi is None:
                poi = POI(**poi_payload)
                session.add(poi)
                created_pois += 1
            else:
                for key, value in poi_payload.items():
                    setattr(poi, key, value)
                updated_pois += 1
                poi.images.clear()
                poi.source_links.clear()

            image_records = list(poi_record.images)
            if poi_record.primary_image is not None and not any(
                image.original_url == poi_record.primary_image.original_url
                and image.thumbnail_url == poi_record.primary_image.thumbnail_url
                for image in image_records
            ):
                image_records.insert(0, poi_record.primary_image)

            poi.images.extend(
                POIImage(**image.model_dump())
                for image in image_records
            )
            poi.source_links.extend(
                POISourceLink(**source_link.model_dump())
                for source_link in poi_record.source_links
            )

        session.commit()

    return {
        "created_cities": created_cities,
        "updated_cities": updated_cities,
        "created_pois": created_pois,
        "updated_pois": updated_pois,
    }


def main() -> None:
    result = seed_database()
    print(
        "Database seeding complete: "
        f"cities +{result['created_cities']} / ~{result['updated_cities']}, "
        f"pois +{result['created_pois']} / ~{result['updated_pois']}"
    )


if __name__ == "__main__":
    main()
