from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.practice_term_model import PracticeTermModel


class PracticeTermRepositoryInterface(ABC):

    @abstractmethod
    async def get_by_id(self, practice_term_id: UUID) -> PracticeTermModel | None:
        ...

    @abstractmethod
    async def get_catalog(self, skip: int = 0, limit: int = 100) -> list[PracticeTermModel]:
        ...

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> list[PracticeTermModel]:
        ...

    @abstractmethod
    async def create(self, practice_term: PracticeTermModel) -> PracticeTermModel:
        ...

    @abstractmethod
    async def update(self, practice_term: PracticeTermModel) -> PracticeTermModel | None:
        ...

    @abstractmethod
    async def delete(self, practice_term_id: UUID) -> bool:
        ...
