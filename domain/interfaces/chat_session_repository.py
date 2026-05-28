from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.chat_session_model import ChatSessionModel


class ChatSessionRepositoryInterface(ABC):

    @abstractmethod
    async def create(self, user_id: UUID, topic: str | None) -> ChatSessionModel:
        ...

    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> ChatSessionModel | None:
        ...

    @abstractmethod
    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 50) -> list[ChatSessionModel]:
        ...

    @abstractmethod
    async def delete(self, session_id: UUID) -> None:
        ...

    @abstractmethod
    async def touch(self, session_id: UUID) -> None:
        """Update updated_at timestamp to now."""
        ...
