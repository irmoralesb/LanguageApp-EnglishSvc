from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.expression_exercise_model import ExpressionExerciseHistoryRecord


class ExpressionExerciseRepositoryInterface(ABC):

    @abstractmethod
    async def save_result(
        self, record: ExpressionExerciseHistoryRecord,
    ) -> ExpressionExerciseHistoryRecord:
        ...

    @abstractmethod
    async def get_history_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[ExpressionExerciseHistoryRecord]:
        ...
