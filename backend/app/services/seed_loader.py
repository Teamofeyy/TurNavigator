import json
from functools import lru_cache
from pathlib import Path

from app.schemas.city import CityBase, CityResponse
from app.schemas.poi import PointOfInterestResponse
from app.services.poi_enrichment import enrich_seed_poi_record

SEEDS_DIR = Path(__file__).resolve().parents[1] / "seeds"


def _read_seed_file(file_name: str) -> list[dict]:
    file_path = SEEDS_DIR / file_name
    return json.loads(file_path.read_text(encoding="utf-8"))


@lru_cache
def get_city_records() -> tuple[CityBase, ...]:
    return tuple(CityBase.model_validate(item) for item in _read_seed_file("cities.json"))


@lru_cache
def get_poi_records() -> tuple[PointOfInterestResponse, ...]:
    return tuple(
        PointOfInterestResponse.model_validate(enrich_seed_poi_record(item))
        for item in _read_seed_file("pois.json")
    )


def list_cities() -> list[CityResponse]:
    pois_by_city = _count_pois_by_city()
    return [
        CityResponse(**city.model_dump(), pois_count=pois_by_city.get(city.id, 0))
        for city in get_city_records()
    ]


def get_city(city_id: int) -> CityResponse | None:
    return next((city for city in list_cities() if city.id == city_id), None)


def list_city_pois(
    city_id: int,
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[PointOfInterestResponse]:
    pois = [poi for poi in get_poi_records() if poi.city_id == city_id]
    if category is not None:
        normalized_category = category.strip().lower()
        pois = [poi for poi in pois if poi.category == normalized_category]
    return pois[offset : offset + limit]


def get_poi(poi_id: int) -> PointOfInterestResponse | None:
    return next((poi for poi in get_poi_records() if poi.id == poi_id), None)


def _count_pois_by_city() -> dict[int, int]:
    counts: dict[int, int] = {}
    for poi in get_poi_records():
        counts[poi.city_id] = counts.get(poi.city_id, 0) + 1
    return counts
