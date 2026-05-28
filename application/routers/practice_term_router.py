from uuid import UUID

from fastapi import APIRouter, Depends, status

from application.routers.dependency_utils import (
    PracticeTermSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.practice_term_schema import (
    PracticeTermCreate,
    PracticeTermUpdate,
    PracticeTermResponse,
)
from domain.entities.practice_term_model import PracticeTermModel

router = APIRouter(
    prefix="/api/v1/prepositions/practice-terms",
    tags=["Prepositions Practice Terms"],
)


@router.get(
    "/catalog",
    response_model=list[PracticeTermResponse],
    dependencies=[Depends(require_role("english-user"))],
)
async def get_catalog(
    svc: PracticeTermSvcDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 100,
):
    items = await svc.get_catalog(skip=skip, limit=limit)
    return [_to_response(i) for i in items]


@router.get(
    "/{practice_term_id}",
    response_model=PracticeTermResponse,
    dependencies=[Depends(require_role("english-user"))],
)
async def get_practice_term(
    practice_term_id: UUID,
    svc: PracticeTermSvcDep,
    current_user: CurrentUserDep,
):
    pt = await svc.get_by_id(practice_term_id)
    return _to_response(pt)


@router.post(
    "/custom",
    response_model=PracticeTermResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("english-user"))],
)
async def create_custom_term(
    payload: PracticeTermCreate,
    svc: PracticeTermSvcDep,
    current_user: CurrentUserDep,
):
    pt = PracticeTermModel(
        id=None,
        term=payload.term,
        term_type=payload.term_type,
        definition=payload.definition,
        example_sentence=payload.example_sentence,
    )
    created = await svc.add_custom_term(current_user.user_id, pt)
    return _to_response(created)


@router.post(
    "/catalog",
    response_model=PracticeTermResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
async def add_to_catalog(
    payload: PracticeTermCreate,
    svc: PracticeTermSvcDep,
    current_user: CurrentUserDep,
):
    pt = PracticeTermModel(
        id=None,
        term=payload.term,
        term_type=payload.term_type,
        definition=payload.definition,
        example_sentence=payload.example_sentence,
    )
    created = await svc.add_to_catalog(pt)
    return _to_response(created)


@router.put(
    "/catalog/{practice_term_id}",
    response_model=PracticeTermResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def update_catalog_term(
    practice_term_id: UUID,
    payload: PracticeTermUpdate,
    svc: PracticeTermSvcDep,
    current_user: CurrentUserDep,
):
    updated = await svc.update_catalog_term(
        practice_term_id=practice_term_id,
        term=payload.term,
        term_type=payload.term_type,
        definition=payload.definition,
        example_sentence=payload.example_sentence,
    )
    return _to_response(updated)


@router.delete(
    "/catalog/{practice_term_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def delete_catalog_term(
    practice_term_id: UUID,
    svc: PracticeTermSvcDep,
    current_user: CurrentUserDep,
):
    await svc.delete_catalog_term(practice_term_id)


def _to_response(pt: PracticeTermModel) -> PracticeTermResponse:
    assert pt.id is not None and pt.created_at is not None
    return PracticeTermResponse(
        id=pt.id,
        term=pt.term,
        term_type=pt.term_type,
        definition=pt.definition,
        example_sentence=pt.example_sentence,
        is_catalog=pt.is_catalog,
        created_by_user_id=pt.created_by_user_id,
        created_at=pt.created_at,
    )
