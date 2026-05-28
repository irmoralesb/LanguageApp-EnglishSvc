from uuid import UUID

from domain.entities.practice_term_model import PracticeTermModel
from domain.exceptions.practice_term_errors import PracticeTermNotFoundError
from domain.interfaces.practice_term_repository import PracticeTermRepositoryInterface


class PracticeTermCatalogService:

    def __init__(self, repo: PracticeTermRepositoryInterface):
        self.repo = repo

    async def get_catalog(self, skip: int = 0, limit: int = 100) -> list[PracticeTermModel]:
        return await self.repo.get_catalog(skip=skip, limit=limit)

    async def get_by_id(self, practice_term_id: UUID) -> PracticeTermModel:
        pt = await self.repo.get_by_id(practice_term_id)
        if pt is None:
            raise PracticeTermNotFoundError(practice_term_id)
        return pt

    async def add_to_catalog(self, pt: PracticeTermModel) -> PracticeTermModel:
        pt.is_catalog = True
        pt.created_by_user_id = None
        return await self.repo.create(pt)

    async def update_catalog_term(
        self,
        practice_term_id: UUID,
        term: str,
        term_type: str,
        definition: str,
        example_sentence: str | None,
    ) -> PracticeTermModel:
        existing = await self.repo.get_by_id(practice_term_id)
        if existing is None:
            raise PracticeTermNotFoundError(practice_term_id)
        existing.term = term
        existing.term_type = term_type
        existing.definition = definition
        existing.example_sentence = example_sentence
        updated = await self.repo.update(existing)
        if updated is None:
            raise PracticeTermNotFoundError(practice_term_id)
        return updated

    async def delete_catalog_term(self, practice_term_id: UUID) -> bool:
        existing = await self.repo.get_by_id(practice_term_id)
        if existing is None:
            raise PracticeTermNotFoundError(practice_term_id)
        return await self.repo.delete(practice_term_id)

    async def add_custom_term(self, user_id: UUID, pt: PracticeTermModel) -> PracticeTermModel:
        pt.is_catalog = False
        pt.created_by_user_id = user_id
        return await self.repo.create(pt)

    async def get_user_custom_terms(self, user_id: UUID) -> list[PracticeTermModel]:
        return await self.repo.get_by_user(user_id)
