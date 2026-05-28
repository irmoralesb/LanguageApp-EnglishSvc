from uuid import UUID

from fastapi import APIRouter, Depends, status

from application.routers.dependency_utils import (
    UserProfileSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.phrasal_user_profile_schema import (
    AddPhrasalVerbSelection,
    PhrasalVerbSelectionResponse,
)

router = APIRouter(
    prefix="/api/v1/phrasal-verbs/profile",
    tags=["Phrasal Verbs Profile"],
    dependencies=[Depends(require_role("english-user"))],
)


@router.get("/phrasal-verbs", response_model=list[PhrasalVerbSelectionResponse])
async def get_selections(
    svc: UserProfileSvcDep,
    current_user: CurrentUserDep,
):
    selections = await svc.get_phrasal_verb_selections(current_user.user_id)
    return [
        PhrasalVerbSelectionResponse(
            id=s.id, user_id=s.user_id,
            phrasal_verb_id=s.phrasal_verb_id, added_at=s.added_at,
        )
        for s in selections
    ]


@router.post(
    "/phrasal-verbs",
    response_model=PhrasalVerbSelectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_selection(
    payload: AddPhrasalVerbSelection,
    svc: UserProfileSvcDep,
    current_user: CurrentUserDep,
):
    sel = await svc.add_phrasal_verb_selection(current_user.user_id, payload.phrasal_verb_id)
    return PhrasalVerbSelectionResponse(
        id=sel.id, user_id=sel.user_id,
        phrasal_verb_id=sel.phrasal_verb_id, added_at=sel.added_at,
    )


@router.delete("/phrasal-verbs/{phrasal_verb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_selection(
    phrasal_verb_id: UUID,
    svc: UserProfileSvcDep,
    current_user: CurrentUserDep,
):
    await svc.remove_phrasal_verb_selection(current_user.user_id, phrasal_verb_id)
