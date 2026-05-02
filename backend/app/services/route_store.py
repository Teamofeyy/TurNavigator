from __future__ import annotations

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import RoutePlan
from app.schemas.route import RoutePlanResponse
from app.services.planning_serialization import route_plan_model_to_response, to_json


def save_route(
    route: RoutePlanResponse,
    *,
    recommendation_run_id: int | None = None,
) -> RoutePlanResponse:
    with SessionLocal() as session:
        route_plan = RoutePlan(
            trip_request_id=route.trip_request_id,
            recommendation_run_id=recommendation_run_id,
            city_id=route.city_id,
            status=route.status,
            total_distance_km=route.total_distance_km,
            total_travel_minutes=route.total_travel_minutes,
            total_visit_minutes=route.total_visit_minutes,
            total_time_minutes=route.total_time_minutes,
            estimated_budget=route.estimated_budget,
            days_count=route.days_count,
            daily_time_limit_minutes=route.daily_time_limit_minutes,
            within_time_limit=route.within_time_limit,
            within_budget=route.within_budget,
            skipped_poi_ids=list(route.skipped_poi_ids),
            route_points=to_json(route.route_points),
            start_location=to_json(route.start_location) if route.start_location else None,
            end_location=to_json(route.end_location) if route.end_location else None,
            return_leg_distance_km=route.return_leg_distance_km,
            return_leg_travel_minutes=route.return_leg_travel_minutes,
            explanation_summary=route.explanation_summary,
        )
        session.add(route_plan)
        session.commit()
        session.refresh(route_plan)
        return route_plan_model_to_response(route_plan)


def get_route(route_id: int) -> RoutePlanResponse | None:
    with SessionLocal() as session:
        statement = select(RoutePlan).where(RoutePlan.id == route_id)
        route = session.scalars(statement).first()
        if route is None:
            return None
        return route_plan_model_to_response(route)
