from uuid import UUID

from fastapi import APIRouter, Depends, status

from application.routers.dependency_utils import (
    UserProfileSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.user_profile_schema import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    AddLearningLanguage,
)

router = APIRouter(
    prefix="/api/v1/profile",
    tags=["User Profile"],
    dependencies=[Depends(require_role("english-user"))],
)


@router.get("", response_model=UserProfileResponse)
async def get_profile(
    svc: UserProfileSvcDep,
    current_user: CurrentUserDep,
):
    profile = await svc.get_profile(current_user.user_id)
    return _profile_response(profile)


@router.post("", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    payload: UserProfileCreate,
    svc: UserProfileSvcDep,
    current_user: CurrentUserDep,
):
    profile = await svc.create_profile(
        user_id=current_user.user_id,
        native_language_id=payload.native_language_id,
        learning_language_ids=payload.learning_language_ids,
    )
    return _profile_response(profile)


@router.put("", response_model=UserProfileResponse)
async def update_profile(
    payload: UserProfileUpdate,
    svc: UserProfileSvcDep,
    current_user: CurrentUserDep,
):
    profile = await svc.update_profile(current_user.user_id, payload.native_language_id)
    return _profile_response(profile)


@router.post("/learning-languages", status_code=status.HTTP_204_NO_CONTENT)
async def add_learning_language(
    payload: AddLearningLanguage,
    svc: UserProfileSvcDep,
    current_user: CurrentUserDep,
):
    await svc.add_learning_language(current_user.user_id, payload.language_id)


@router.delete("/learning-languages/{language_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_learning_language(
    language_id: UUID,
    svc: UserProfileSvcDep,
    current_user: CurrentUserDep,
):
    await svc.remove_learning_language(current_user.user_id, language_id)


def _profile_response(profile) -> UserProfileResponse:
    return UserProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        native_language_id=profile.native_language_id,
        learning_language_ids=profile.learning_language_ids,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )
