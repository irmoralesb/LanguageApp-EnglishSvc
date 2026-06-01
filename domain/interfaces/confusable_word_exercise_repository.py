from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.confusable_word_exercise_model import (
    ConfusableWordHistoryRecord,
    ConfusableWordPairStats,
)


class ConfusableWordExerciseRepositoryInterface(ABC):

    @abstractmethod
    async def save_result(
        self, record: ConfusableWordHistoryRecord,
    ) -> ConfusableWordHistoryRecord:
        ...

    @abstractmethod
    async def get_history_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[ConfusableWordHistoryRecord]:
        ...

    @abstractmethod
    async def get_pair_stats_by_user(self, user_id: UUID) -> list[ConfusableWordPairStats]:
        ...
