from uuid import UUID

from fastapi import APIRouter, Depends, status

from application.routers.dependency_utils import (
    EnglishExpressionSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.english_expression_schema import (
    EnglishExpressionCreate,
    EnglishExpressionUpdate,
    EnglishExpressionResponse,
)
from domain.entities.english_expression_model import EnglishExpressionModel

router = APIRouter(
    prefix="/api/v1/expressions",
    tags=["English Expressions"],
)


@router.get(
    "/catalog",
    response_model=list[EnglishExpressionResponse],
    dependencies=[Depends(require_role("english-user"))],
)
async def get_catalog(
    svc: EnglishExpressionSvcDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 100,
    expression_type: str | None = None,
):
    items = await svc.get_catalog(skip=skip, limit=limit, expression_type=expression_type)
    return [_to_response(i) for i in items]


@router.get(
    "/{english_expression_id}",
    response_model=EnglishExpressionResponse,
    dependencies=[Depends(require_role("english-user"))],
)
async def get_expression(
    english_expression_id: UUID,
    svc: EnglishExpressionSvcDep,
    current_user: CurrentUserDep,
):
    expr = await svc.get_by_id(english_expression_id)
    return _to_response(expr)


@router.post(
    "/custom",
    response_model=EnglishExpressionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("english-user"))],
)
async def create_custom_expression(
    payload: EnglishExpressionCreate,
    svc: EnglishExpressionSvcDep,
    current_user: CurrentUserDep,
):
    expr = EnglishExpressionModel(
        id=None,
        text=payload.text,
        expression_type=payload.expression_type,
        definition=payload.definition,
        example_sentence=payload.example_sentence,
        register=payload.register,
    )
    created = await svc.add_custom_expression(current_user.user_id, expr)
    return _to_response(created)


@router.post(
    "/catalog",
    response_model=EnglishExpressionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
async def add_to_catalog(
    payload: EnglishExpressionCreate,
    svc: EnglishExpressionSvcDep,
    current_user: CurrentUserDep,
):
    expr = EnglishExpressionModel(
        id=None,
        text=payload.text,
        expression_type=payload.expression_type,
        definition=payload.definition,
        example_sentence=payload.example_sentence,
        register=payload.register,
    )
    created = await svc.add_to_catalog(expr)
    return _to_response(created)


@router.put(
    "/catalog/{english_expression_id}",
    response_model=EnglishExpressionResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def update_catalog_expression(
    english_expression_id: UUID,
    payload: EnglishExpressionUpdate,
    svc: EnglishExpressionSvcDep,
    current_user: CurrentUserDep,
):
    updated = await svc.update_catalog_expression(
        english_expression_id=english_expression_id,
        text=payload.text,
        expression_type=payload.expression_type,
        definition=payload.definition,
        example_sentence=payload.example_sentence,
        register=payload.register,
    )
    return _to_response(updated)


@router.delete(
    "/catalog/{english_expression_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def delete_catalog_expression(
    english_expression_id: UUID,
    svc: EnglishExpressionSvcDep,
    current_user: CurrentUserDep,
):
    await svc.delete_catalog_expression(english_expression_id)


def _to_response(expr: EnglishExpressionModel) -> EnglishExpressionResponse:
    return EnglishExpressionResponse(
        id=expr.id,  # type: ignore[arg-type]
        text=expr.text,
        expression_type=expr.expression_type,
        definition=expr.definition,
        example_sentence=expr.example_sentence,
        register=expr.register,
        is_catalog=expr.is_catalog,
        created_by_user_id=expr.created_by_user_id,
        created_at=expr.created_at,
    )
