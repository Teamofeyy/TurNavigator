from __future__ import annotations

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import UserProfile
from app.schemas.profile import UserProfileCreate, UserProfileResponse, UserProfileUpdate
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
            .order_by(UserProfile.updated_at.desc(), UserProfile.created_at.desc())
            .limit(limit)
        )
        profiles = session.scalars(statement).all()
        return [profile_model_to_response(profile) for profile in profiles]


def update_profile(profile_id: int, payload: UserProfileUpdate) -> UserProfileResponse | None:
    with SessionLocal() as session:
        profile = session.get(UserProfile, profile_id)
        if profile is None:
            return None

        for field_name, value in payload.model_dump(exclude_unset=True).items():
            setattr(profile, field_name, value)

        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile_model_to_response(profile)
