from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.multiple_prepositions_exercise_model import (
    MultiplePrepositionsExerciseHistoryRecord,
)


class MultiplePrepositionsExerciseRepositoryInterface(ABC):

    @abstractmethod
    async def save_attempt(
        self, record: MultiplePrepositionsExerciseHistoryRecord,
    ) -> MultiplePrepositionsExerciseHistoryRecord:
        ...

    @abstractmethod
    async def get_history_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[MultiplePrepositionsExerciseHistoryRecord]:
        ...
