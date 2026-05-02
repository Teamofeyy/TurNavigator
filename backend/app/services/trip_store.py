from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models import TripRequest, UserProfile
from app.schemas.planning import TripRequestCreate, TripRequestResponse
from app.services.planning_serialization import to_json, trip_request_model_to_response
from app.services.profile_store import create_profile_record


def create_trip_request(payload: TripRequestCreate) -> TripRequestResponse:
    with SessionLocal() as session:
        if payload.profile_id is not None:
            profile = session.get(UserProfile, payload.profile_id)
            if profile is None:
                raise LookupError("Profile not found")
        else:
            assert payload.profile is not None
            profile = create_profile_record(session, payload.profile)

        selected_interests = payload.selected_interests or list(profile.interests)
        trip_request = TripRequest(
            city_id=payload.city_id,
            profile_id=profile.id,
            days_count=payload.days_count,
            daily_time_limit_hours=payload.daily_time_limit_hours,
            selected_interests=selected_interests,
            constraints=to_json(payload.constraints),
            start_location=to_json(payload.start_location) if payload.start_location else None,
            end_location=to_json(payload.end_location) if payload.end_location else None,
            profile_snapshot=to_json(
                {
                    "id": profile.id,
                    "interests": list(profile.interests),
                    "budget_level": profile.budget_level,
                    "max_budget": profile.max_budget,
                    "pace": profile.pace,
                    "max_walking_distance_km": profile.max_walking_distance_km,
                    "preferred_transport": profile.preferred_transport,
                    "explanation_level": profile.explanation_level,
                    "goals": list(profile.goals),
                    "must_have": list(profile.must_have),
                    "avoid": list(profile.avoid),
                    "compromise_strategy": profile.compromise_strategy,
                    "trust_level": profile.trust_level,
                    "accessibility_needs": list(profile.accessibility_needs),
                    "preferred_time_windows": list(profile.preferred_time_windows),
                    "created_at": profile.created_at,
                    "updated_at": profile.updated_at,
                }
            ),
        )
        session.add(trip_request)
        session.commit()
        session.refresh(trip_request)
        session.refresh(profile)
        trip_request.profile = profile
        return trip_request_model_to_response(trip_request)


def get_trip_request(trip_request_id: int) -> TripRequestResponse | None:
    with SessionLocal() as session:
        statement = (
            select(TripRequest)
            .where(TripRequest.id == trip_request_id)
            .options(selectinload(TripRequest.profile))
        )
        trip_request = session.scalars(statement).first()
        if trip_request is None:
            return None
        return trip_request_model_to_response(trip_request)
