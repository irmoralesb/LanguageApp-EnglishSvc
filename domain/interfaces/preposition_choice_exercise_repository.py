from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.preposition_choice_exercise_model import (
    PrepositionChoiceHistoryRecord,
    PrepositionChoicePairStats,
)


class PrepositionChoiceExerciseRepositoryInterface(ABC):

    @abstractmethod
    async def save_result(
        self, record: PrepositionChoiceHistoryRecord,
    ) -> PrepositionChoiceHistoryRecord:
        ...

    @abstractmethod
    async def get_history_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[PrepositionChoiceHistoryRecord]:
        ...

    @abstractmethod
    async def get_pair_stats_by_user(self, user_id: UUID) -> list[PrepositionChoicePairStats]:
        ...
