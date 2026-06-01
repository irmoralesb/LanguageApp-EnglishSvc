from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.natural_rewrite_exercise_model import NaturalRewriteHistoryRecord


class NaturalRewriteExerciseRepositoryInterface(ABC):

    @abstractmethod
    async def save_result(
        self, record: NaturalRewriteHistoryRecord,
    ) -> NaturalRewriteHistoryRecord:
        ...

    @abstractmethod
    async def get_history_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[NaturalRewriteHistoryRecord]:
        ...
