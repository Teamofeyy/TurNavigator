from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.profile import UserProfileCreate, UserProfileResponse, UserProfileUpdate
from app.services.profile_store import create_profile, get_profile, list_profiles, update_profile

router = APIRouter(tags=["profiles"])


@router.post(
    "/profiles",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a reusable user profile",
    description=(
        "Persists an expanded digital consciousness profile with goals, "
        "constraints, and accessibility preferences."
    ),
    response_description="Created profile.",
)
async def create_profile_endpoint(payload: UserProfileCreate) -> UserProfileResponse:
    return create_profile(payload)


@router.get(
    "/profiles",
    response_model=list[UserProfileResponse],
    summary="List saved user profiles",
    description="Returns the most recent reusable planning profiles.",
    response_description="Saved profiles.",
)
async def list_profiles_endpoint(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of profiles to return.",
    ),
) -> list[UserProfileResponse]:
    return list_profiles(limit=limit)


@router.get(
    "/profiles/{profile_id}",
    response_model=UserProfileResponse,
    summary="Get saved profile by id",
    description="Returns one persisted planning profile.",
    response_description="Saved profile.",
    responses={
        404: {
            "description": "Profile was not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Profile not found"},
                },
            },
        },
    },
)
async def get_profile_endpoint(profile_id: int) -> UserProfileResponse:
    profile = get_profile(profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return profile


@router.patch(
    "/profiles/{profile_id}",
    response_model=UserProfileResponse,
    summary="Update saved profile",
    description=(
        "Updates one reusable MVP profile. The endpoint is intended for demo flows "
        "without a full user account system."
    ),
    response_description="Updated profile.",
    responses={
        404: {
            "description": "Profile was not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Profile not found"},
                },
            },
        },
    },
)
async def update_profile_endpoint(
    profile_id: int,
    payload: UserProfileUpdate,
) -> UserProfileResponse:
    profile = update_profile(profile_id, payload)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return profile
