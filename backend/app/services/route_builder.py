from math import asin, ceil, cos, radians, sin, sqrt

from app.schemas.planning import TripLocationResponse
from app.schemas.city import CityResponse
from app.schemas.planning import TripRequestResponse
from app.schemas.poi import PointOfInterestResponse
from app.schemas.route import RoutePlanResponse, RoutePointResponse, RouteStatus

TRAVEL_SPEED_KMH: dict[str, float] = {
    "walking": 4.5,
    "public_transport": 18.0,
    "car": 28.0,
    "mixed": 12.0,
}


def build_route_plan(
    trip_request: TripRequestResponse,
    city: CityResponse,
    pois: list[PointOfInterestResponse],
    optimize_order: bool,
    strict_constraints: bool,
    start_location: TripLocationResponse | None = None,
    end_location: TripLocationResponse | None = None,
) -> RoutePlanResponse:
    resolved_start = start_location or _city_center_location(city)
    resolved_end = end_location or resolved_start
    ordered_pois = (
        _nearest_neighbor_order(start_location=resolved_start, pois=pois)
        if optimize_order
        else pois
    )

    route_points: list[RoutePointResponse] = []
    skipped_poi_ids: list[int] = []
    current_lat = resolved_start.latitude
    current_lon = resolved_start.longitude
    total_distance_km = 0.0
    total_travel_minutes = 0
    total_visit_minutes = 0
    total_budget = 0
    total_time_limit = trip_request.days_count * trip_request.daily_time_limit_hours * 60

    for poi in ordered_pois:
        leg_distance_km = _distance_km(current_lat, current_lon, poi.latitude, poi.longitude)
        leg_travel_minutes = _travel_minutes(
            distance_km=leg_distance_km,
            transport=trip_request.profile.preferred_transport,
        )
        next_total_time = (
            total_travel_minutes
            + total_visit_minutes
            + leg_travel_minutes
            + poi.estimated_visit_minutes
        )
        next_total_budget = total_budget + poi.average_cost_rub

        if strict_constraints and (
            next_total_time > total_time_limit
            or next_total_budget > trip_request.profile.max_budget
        ):
            skipped_poi_ids.append(poi.id)
            continue

        total_distance_km += leg_distance_km
        total_travel_minutes += leg_travel_minutes
        total_visit_minutes += poi.estimated_visit_minutes
        total_budget = next_total_budget
        current_lat = poi.latitude
        current_lon = poi.longitude

        route_points.append(
            RoutePointResponse(
                order=len(route_points) + 1,
                poi_id=poi.id,
                name=poi.name,
                category=poi.category,
                latitude=poi.latitude,
                longitude=poi.longitude,
                leg_distance_km=round(leg_distance_km, 2),
                leg_travel_minutes=leg_travel_minutes,
                visit_minutes=poi.estimated_visit_minutes,
                estimated_cost_rub=poi.average_cost_rub,
                cumulative_distance_km=round(total_distance_km, 2),
                cumulative_time_minutes=total_travel_minutes + total_visit_minutes,
                cumulative_budget_rub=total_budget,
                poi=poi,
            )
        )

    return_leg_distance_km = 0.0
    return_leg_travel_minutes = 0
    if route_points:
        return_leg_distance_km = _distance_km(
            current_lat,
            current_lon,
            resolved_end.latitude,
            resolved_end.longitude,
        )
        return_leg_travel_minutes = _travel_minutes(
            distance_km=return_leg_distance_km,
            transport=trip_request.profile.preferred_transport,
        )
        total_distance_km += return_leg_distance_km
        total_travel_minutes += return_leg_travel_minutes

    total_time_minutes = total_travel_minutes + total_visit_minutes
    within_time_limit = total_time_minutes <= total_time_limit
    within_budget = total_budget <= trip_request.profile.max_budget
    status = _route_status(route_points=route_points, skipped_poi_ids=skipped_poi_ids)

    return RoutePlanResponse(
        id=0,
        trip_request_id=trip_request.id,
        city_id=trip_request.city_id,
        status=status,
        total_distance_km=round(total_distance_km, 2),
        total_travel_minutes=total_travel_minutes,
        total_visit_minutes=total_visit_minutes,
        total_time_minutes=total_time_minutes,
        estimated_budget=total_budget,
        days_count=trip_request.days_count,
        daily_time_limit_minutes=trip_request.daily_time_limit_hours * 60,
        within_time_limit=within_time_limit,
        within_budget=within_budget,
        start_location=resolved_start,
        end_location=resolved_end,
        return_leg_distance_km=round(return_leg_distance_km, 2),
        return_leg_travel_minutes=return_leg_travel_minutes,
        skipped_poi_ids=skipped_poi_ids,
        route_points=route_points,
        explanation_summary=_explain_route(
            route_points=route_points,
            skipped_poi_ids=skipped_poi_ids,
            total_distance_km=total_distance_km,
            total_time_minutes=total_time_minutes,
            total_budget=total_budget,
            within_time_limit=within_time_limit,
            within_budget=within_budget,
            start_location=resolved_start,
            end_location=resolved_end,
            return_leg_distance_km=return_leg_distance_km,
        ),
    )


def _nearest_neighbor_order(
    start_location: TripLocationResponse,
    pois: list[PointOfInterestResponse],
) -> list[PointOfInterestResponse]:
    if not pois:
        return []

    ordered: list[PointOfInterestResponse] = []
    remaining = list(pois)
    current_lat = start_location.latitude
    current_lon = start_location.longitude
    while remaining:
        nearest = min(
            remaining,
            key=lambda poi: _distance_km(current_lat, current_lon, poi.latitude, poi.longitude),
        )
        ordered.append(nearest)
        remaining.remove(nearest)
        current_lat = nearest.latitude
        current_lon = nearest.longitude
    return ordered


def _travel_minutes(distance_km: float, transport: str) -> int:
    speed_kmh = TRAVEL_SPEED_KMH.get(transport, TRAVEL_SPEED_KMH["mixed"])
    if distance_km == 0:
        return 0
    return max(1, ceil((distance_km / speed_kmh) * 60))


def _route_status(
    route_points: list[RoutePointResponse],
    skipped_poi_ids: list[int],
) -> RouteStatus:
    if not route_points:
        return "empty"
    if skipped_poi_ids:
        return "partially_built"
    return "built"


def _explain_route(
    route_points: list[RoutePointResponse],
    skipped_poi_ids: list[int],
    total_distance_km: float,
    total_time_minutes: int,
    total_budget: int,
    within_time_limit: bool,
    within_budget: bool,
    start_location: TripLocationResponse,
    end_location: TripLocationResponse,
    return_leg_distance_km: float,
) -> str:
    if not route_points:
        return "Маршрут не построен: все кандидаты превысили ограничения по времени или бюджету."

    parts = [
        f"старт {start_location.name or start_location.address}",
        f"финиш {end_location.name or end_location.address}",
        f"маршрут включает {len(route_points)} точек",
        f"примерная дистанция {round(total_distance_km, 2)} км",
        f"общее время {total_time_minutes} мин.",
        f"ориентировочный бюджет {total_budget} руб.",
    ]
    if return_leg_distance_km > 0:
        parts.append(f"возврат до финальной точки {round(return_leg_distance_km, 2)} км")
    parts.append("вписывается во временное ограничение" if within_time_limit else "превышает временное ограничение")
    parts.append("вписывается в бюджет" if within_budget else "превышает бюджет")
    if skipped_poi_ids:
        parts.append(f"часть объектов пропущена из-за ограничений: {', '.join(map(str, skipped_poi_ids))}")
    return "Модуль построения маршрута сформировал маршрут: " + "; ".join(parts) + "."


def _city_center_location(city: CityResponse) -> TripLocationResponse:
    return TripLocationResponse(
        name=f"Центр {city.name}",
        address=f"Центр города {city.name}",
        latitude=city.latitude,
        longitude=city.longitude,
        poi_id=None,
    )


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    )
    return 2 * earth_radius_km * asin(sqrt(a))
