from __future__ import annotations

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import UserProfile
from app.schemas.profile import UserProfileCreate, UserProfileResponse
from app.services.planning_serialization import profile_model_to_response


def create_profile(payload: UserProfileCreate) -> UserProfileResponse:
    with SessionLocal() as session:
        profile = create_profile_record(session, payload)
        session.commit()
        session.refresh(profile)
        return profile_model_to_response(profile)


def create_profile_record(session, payload: UserProfileCreate) -> UserProfile:
    profile = UserProfile(**payload.model_dump())
    session.add(profile)
    session.flush()
    session.refresh(profile)
    return profile


def get_profile(profile_id: int) -> UserProfileResponse | None:
    with SessionLocal() as session:
        profile = session.get(UserProfile, profile_id)
        if profile is None:
            return None
        return profile_model_to_response(profile)


def list_profiles(limit: int = 20) -> list[UserProfileResponse]:
    with SessionLocal() as session:
        statement = (
            select(UserProfile)
            .order_by(UserProfile.created_at.desc())
            .limit(limit)
        )
        profiles = session.scalars(statement).all()
        return [profile_model_to_response(profile) for profile in profiles]
