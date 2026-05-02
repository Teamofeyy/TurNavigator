from __future__ import annotations

import json
from collections import Counter

from app.services.seed_loader import get_poi_records


def build_report() -> dict[str, object]:
    pois = list(get_poi_records())
    interest_sources = Counter(poi.interest_source for poi in pois)
    category_counts = Counter(poi.category for poi in pois)

    coverage = {
        "with_website": sum(1 for poi in pois if poi.website),
        "with_phone": sum(1 for poi in pois if poi.phone),
        "with_wikidata": sum(1 for poi in pois if poi.wikidata_id),
        "with_wikipedia": sum(1 for poi in pois if poi.wikipedia_url or poi.wikipedia_title),
        "with_images": sum(1 for poi in pois if poi.primary_image or poi.images),
        "with_source_links": sum(1 for poi in pois if poi.source_links),
    }
    averages = {
        "popularity_score": round(
            sum(poi.popularity_score for poi in pois) / max(len(pois), 1),
            2,
        ),
        "data_quality_score": round(
            sum(poi.data_quality_score for poi in pois) / max(len(pois), 1),
            2,
        ),
    }

    return {
        "total_pois": len(pois),
        "interest_sources": dict(sorted(interest_sources.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "coverage": coverage,
        "averages": averages,
    }


def main() -> None:
    print(
        json.dumps(
            build_report(),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
