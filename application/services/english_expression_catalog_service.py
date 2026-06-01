from uuid import UUID

from domain.entities.english_expression_model import EnglishExpressionModel
from domain.exceptions.english_expression_errors import EnglishExpressionNotFoundError
from domain.interfaces.english_expression_repository import EnglishExpressionRepositoryInterface


class EnglishExpressionCatalogService:

    def __init__(self, repo: EnglishExpressionRepositoryInterface):
        self.repo = repo

    async def get_catalog(
        self,
        skip: int = 0,
        limit: int = 100,
        expression_type: str | None = None,
    ) -> list[EnglishExpressionModel]:
        return await self.repo.get_catalog(
            skip=skip, limit=limit, expression_type=expression_type,
        )

    async def get_by_id(self, english_expression_id: UUID) -> EnglishExpressionModel:
        expr = await self.repo.get_by_id(english_expression_id)
        if expr is None:
            raise EnglishExpressionNotFoundError(english_expression_id)
        return expr

    async def add_to_catalog(self, expression: EnglishExpressionModel) -> EnglishExpressionModel:
        expression.is_catalog = True
        expression.created_by_user_id = None
        return await self.repo.create(expression)

    async def update_catalog_expression(
        self,
        english_expression_id: UUID,
        text: str,
        expression_type: str,
        definition: str,
        example_sentence: str | None,
        register: str,
    ) -> EnglishExpressionModel:
        existing = await self.repo.get_by_id(english_expression_id)
        if existing is None:
            raise EnglishExpressionNotFoundError(english_expression_id)
        existing.text = text
        existing.expression_type = expression_type
        existing.definition = definition
        existing.example_sentence = example_sentence
        existing.register = register
        updated = await self.repo.update(existing)
        if updated is None:
            raise EnglishExpressionNotFoundError(english_expression_id)
        return updated

    async def delete_catalog_expression(self, english_expression_id: UUID) -> bool:
        existing = await self.repo.get_by_id(english_expression_id)
        if existing is None:
            raise EnglishExpressionNotFoundError(english_expression_id)
        return await self.repo.delete(english_expression_id)

    async def add_custom_expression(
        self, user_id: UUID, expression: EnglishExpressionModel,
    ) -> EnglishExpressionModel:
        expression.is_catalog = False
        expression.created_by_user_id = user_id
        return await self.repo.create(expression)

    async def get_user_custom_expressions(self, user_id: UUID) -> list[EnglishExpressionModel]:
        return await self.repo.get_by_user(user_id)
