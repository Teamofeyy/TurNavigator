from __future__ import annotations

from app.schemas.city import CityResponse
from app.schemas.poi import PointOfInterestResponse
from app.services import seed_loader
from app.services.catalog_repository import (
    database_catalog_available,
    get_city_from_db,
    get_poi_from_db,
    list_cities_from_db,
    list_city_pois_from_db,
)


def list_cities() -> list[CityResponse]:
    if database_catalog_available():
        return list_cities_from_db()
    return seed_loader.list_cities()


def get_city(city_id: int) -> CityResponse | None:
    if database_catalog_available():
        city = get_city_from_db(city_id)
        if city is not None:
            return city
    return seed_loader.get_city(city_id)


def list_city_pois(
    city_id: int,
    *,
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[PointOfInterestResponse]:
    if database_catalog_available():
        pois = list_city_pois_from_db(
            city_id,
            category=category,
            limit=limit,
            offset=offset,
        )
        if pois:
            return pois
    return seed_loader.list_city_pois(
        city_id,
        category=category,
        limit=limit,
        offset=offset,
    )


def get_poi(poi_id: int) -> PointOfInterestResponse | None:
    if database_catalog_available():
        poi = get_poi_from_db(poi_id)
        if poi is not None:
            return poi
    return seed_loader.get_poi(poi_id)
