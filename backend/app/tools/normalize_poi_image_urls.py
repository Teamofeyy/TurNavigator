from __future__ import annotations

from app.db.session import SessionLocal
from app.models import POIImage
from app.services.media_urls import normalize_poi_image_url


def main() -> None:
    changed_rows = 0
    changed_values = 0

    with SessionLocal() as session:
        images = session.query(POIImage).order_by(POIImage.id.asc()).all()
        for image in images:
            changed = False

            normalized_original = normalize_poi_image_url(image.original_url)
            if normalized_original != image.original_url:
                image.original_url = normalized_original
                changed = True
                changed_values += 1

            normalized_thumbnail = normalize_poi_image_url(image.thumbnail_url)
            if normalized_thumbnail != image.thumbnail_url:
                image.thumbnail_url = normalized_thumbnail
                changed = True
                changed_values += 1

            if changed:
                changed_rows += 1

        session.commit()

    print(
        "Normalized POI image URLs: "
        f"{changed_rows} rows, {changed_values} fields changed."
    )


if __name__ == "__main__":
    main()
