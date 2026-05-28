from uuid import UUID

from fastapi import APIRouter, Depends, status

from application.routers.dependency_utils import (
    CurrentUserDep,
    UserProfileSvcDep,
    require_role,
)
from application.schemas.user_profile_schema import (
    AddPracticeTermSelection,
    PracticeTermSelectionResponse,
)

router = APIRouter(
    prefix="/api/v1/prepositions/profile",
    tags=["Prepositions Profile"],
    dependencies=[Depends(require_role("english-user"))],
)


@router.get("/practice-terms", response_model=list[PracticeTermSelectionResponse])
async def get_selections(
    svc: UserProfileSvcDep,
    current_user: CurrentUserDep,
):
    selections = await svc.get_practice_term_selections(current_user.user_id)
    return [
        PracticeTermSelectionResponse(
            id=s.id,
            user_id=s.user_id,
            practice_term_id=s.practice_term_id,
            added_at=s.added_at,
        )
        for s in selections
    ]


@router.post(
    "/practice-terms",
    response_model=PracticeTermSelectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_selection(
    payload: AddPracticeTermSelection,
    svc: UserProfileSvcDep,
    current_user: CurrentUserDep,
):
    sel = await svc.add_practice_term_selection(current_user.user_id, payload.practice_term_id)
    return PracticeTermSelectionResponse(
        id=sel.id,
        user_id=sel.user_id,
        practice_term_id=sel.practice_term_id,
        added_at=sel.added_at,
    )


@router.delete("/practice-terms/{practice_term_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_selection(
    practice_term_id: UUID,
    svc: UserProfileSvcDep,
    current_user: CurrentUserDep,
):
    await svc.remove_practice_term_selection(current_user.user_id, practice_term_id)
