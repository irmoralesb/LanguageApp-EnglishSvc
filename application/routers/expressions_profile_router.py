from uuid import UUID

from fastapi import APIRouter, Depends, status

from application.routers.dependency_utils import (
    UserProfileSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.expressions_profile_schema import (
    AddEnglishExpressionSelection,
    EnglishExpressionSelectionResponse,
)

router = APIRouter(
    prefix="/api/v1/expressions/profile",
    tags=["Expressions Profile"],
    dependencies=[Depends(require_role("english-user"))],
)


@router.get("/expressions", response_model=list[EnglishExpressionSelectionResponse])
async def get_selections(
    svc: UserProfileSvcDep,
    current_user: CurrentUserDep,
):
    selections = await svc.get_english_expression_selections(current_user.user_id)
    return [
        EnglishExpressionSelectionResponse(
            id=s.id,  # type: ignore[arg-type]
            user_id=s.user_id,
            english_expression_id=s.english_expression_id,
            added_at=s.added_at,
        )
        for s in selections
    ]


@router.post(
    "/expressions",
    response_model=EnglishExpressionSelectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_selection(
    payload: AddEnglishExpressionSelection,
    svc: UserProfileSvcDep,
    current_user: CurrentUserDep,
):
    sel = await svc.add_english_expression_selection(
        current_user.user_id, payload.english_expression_id,
    )
    return EnglishExpressionSelectionResponse(
        id=sel.id,  # type: ignore[arg-type]
        user_id=sel.user_id,
        english_expression_id=sel.english_expression_id,
        added_at=sel.added_at,
    )


@router.delete("/expressions/{english_expression_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_selection(
    english_expression_id: UUID,
    svc: UserProfileSvcDep,
    current_user: CurrentUserDep,
):
    await svc.remove_english_expression_selection(
        current_user.user_id, english_expression_id,
    )
