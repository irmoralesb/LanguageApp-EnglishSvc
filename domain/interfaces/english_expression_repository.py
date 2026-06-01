from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.english_expression_model import EnglishExpressionModel


class EnglishExpressionRepositoryInterface(ABC):

    @abstractmethod
    async def get_by_id(self, english_expression_id: UUID) -> EnglishExpressionModel | None:
        ...

    @abstractmethod
    async def get_catalog(
        self, skip: int = 0, limit: int = 100, expression_type: str | None = None,
    ) -> list[EnglishExpressionModel]:
        ...

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> list[EnglishExpressionModel]:
        ...

    @abstractmethod
    async def create(self, expression: EnglishExpressionModel) -> EnglishExpressionModel:
        ...

    @abstractmethod
    async def update(self, expression: EnglishExpressionModel) -> EnglishExpressionModel | None:
        ...

    @abstractmethod
    async def delete(self, english_expression_id: UUID) -> bool:
        ...
