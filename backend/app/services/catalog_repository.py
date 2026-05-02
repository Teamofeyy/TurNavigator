from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models import City, POI
from app.schemas.city import CityResponse
from app.schemas.poi import POIImage, POISourceLink, PointOfInterestResponse


def list_cities_from_db() -> list[CityResponse]:
    with SessionLocal() as session:
        poi_counts_subquery = (
            select(POI.city_id, func.count(POI.id).label("pois_count"))
            .group_by(POI.city_id)
            .subquery()
        )
        statement = (
            select(City, func.coalesce(poi_counts_subquery.c.pois_count, 0))
            .outerjoin(poi_counts_subquery, poi_counts_subquery.c.city_id == City.id)
            .order_by(City.name.asc())
        )
        rows = session.execute(statement).all()
        return [
            _city_to_response(city, pois_count=pois_count)
            for city, pois_count in rows
        ]


def get_city_from_db(city_id: int) -> CityResponse | None:
    with SessionLocal() as session:
        poi_count = session.execute(
            select(func.count(POI.id)).where(POI.city_id == city_id)
        ).scalar_one()
        city = session.get(City, city_id)
        if city is None:
            return None
        return _city_to_response(city, pois_count=poi_count)


def list_city_pois_from_db(
    city_id: int,
    *,
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[PointOfInterestResponse]:
    with SessionLocal() as session:
        statement = (
            select(POI)
            .where(POI.city_id == city_id)
            .options(
                selectinload(POI.images),
                selectinload(POI.source_links),
            )
            .order_by(POI.popularity_score.desc(), POI.name.asc())
            .limit(limit)
            .offset(offset)
        )
        if category is not None:
            statement = statement.where(POI.category == category.strip().lower())
        pois = session.scalars(statement).all()
        return [_poi_to_response(poi) for poi in pois]


def get_poi_from_db(poi_id: int) -> PointOfInterestResponse | None:
    with SessionLocal() as session:
        statement = (
            select(POI)
            .where(POI.id == poi_id)
            .options(
                selectinload(POI.images),
                selectinload(POI.source_links),
            )
        )
        poi = session.scalars(statement).first()
        if poi is None:
            return None
        return _poi_to_response(poi)


def database_catalog_available() -> bool:
    try:
        with SessionLocal() as session:
            city_count = session.execute(select(func.count(City.id))).scalar_one()
            return city_count > 0
    except SQLAlchemyError:
        return False


def _city_to_response(city: City, *, pois_count: int) -> CityResponse:
    return CityResponse(
        id=city.id,
        name=city.name,
        region=city.region,
        country=city.country,
        latitude=city.latitude,
        longitude=city.longitude,
        population=city.population,
        source=city.source,
        external_id=city.external_id,
        wikidata_id=city.wikidata_id,
        osm_id=city.osm_id,
        pois_count=pois_count,
    )


def _poi_to_response(poi: POI) -> PointOfInterestResponse:
    image_models = list(_images_to_schema(poi.images))
    primary_image = next((image for image in image_models if image.is_primary), None)
    if primary_image is None and image_models:
        image_models[0].is_primary = True
        primary_image = image_models[0]

    return PointOfInterestResponse(
        id=poi.id,
        city_id=poi.city_id,
        name=poi.name,
        category=poi.category,
        subcategory=poi.subcategory,
        latitude=poi.latitude,
        longitude=poi.longitude,
        address=poi.address,
        description=poi.description,
        opening_hours=poi.opening_hours,
        website=poi.website,
        phone=poi.phone,
        source=poi.source,
        external_id=poi.external_id,
        wikidata_id=poi.wikidata_id,
        wikipedia_title=poi.wikipedia_title,
        wikipedia_url=poi.wikipedia_url,
        wikimedia_commons=poi.wikimedia_commons,
        osm_tags=poi.osm_tags,
        estimated_price_level=poi.estimated_price_level,
        average_cost_rub=poi.average_cost_rub,
        estimated_visit_minutes=poi.estimated_visit_minutes,
        popularity_score=poi.popularity_score,
        data_quality_score=poi.data_quality_score,
        interests=poi.interests,
        interest_source=poi.interest_source,
        primary_image=primary_image,
        images=image_models,
        source_links=list(_source_links_to_schema(poi.source_links)),
        data_freshness_days=poi.data_freshness_days,
        last_enriched_at=poi.last_enriched_at,
    )


def _images_to_schema(images: Iterable) -> Iterable[POIImage]:
    for image in images:
        yield POIImage(
            provider=image.provider,
            original_url=image.original_url,
            thumbnail_url=image.thumbnail_url,
            source_page_url=image.source_page_url,
            license=image.license,
            author=image.author,
            attribution_text=image.attribution_text,
            width=image.width,
            height=image.height,
            is_primary=image.is_primary,
        )


def _source_links_to_schema(source_links: Iterable) -> Iterable[POISourceLink]:
    for link in source_links:
        yield POISourceLink(
            provider=link.provider,
            external_id=link.external_id,
            url=link.url,
            license=link.license,
            last_synced_at=link.last_synced_at,
        )
