from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.register_switch_exercise_model import RegisterSwitchHistoryRecord


class RegisterSwitchExerciseRepositoryInterface(ABC):

    @abstractmethod
    async def save_result(
        self, record: RegisterSwitchHistoryRecord,
    ) -> RegisterSwitchHistoryRecord:
        ...

    @abstractmethod
    async def get_history_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[RegisterSwitchHistoryRecord]:
        ...
