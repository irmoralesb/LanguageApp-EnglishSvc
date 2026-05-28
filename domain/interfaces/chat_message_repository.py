from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.chat_message_model import ChatMessageModel
from domain.entities.message_feedback_model import MessageFeedbackModel


class ChatMessageRepositoryInterface(ABC):

    @abstractmethod
    async def create_message(self, session_id: UUID, role: str, content: str) -> ChatMessageModel:
        ...

    @abstractmethod
    async def create_feedback(
        self,
        message_id: UUID,
        corrections_json: str,
        recommendations_json: str,
    ) -> MessageFeedbackModel:
        ...

    @abstractmethod
    async def list_by_session(self, session_id: UUID) -> list[ChatMessageModel]:
        ...
