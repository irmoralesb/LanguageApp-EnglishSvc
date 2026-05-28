import asyncio
import json
import logging
from dataclasses import asdict
from uuid import UUID

from domain.entities.chat_message_model import ChatMessageModel
from domain.entities.chat_session_model import ChatSessionModel
from domain.entities.message_feedback_model import MessageFeedbackModel
from domain.exceptions.chat_errors import ChatSessionNotFoundError, ChatSessionAccessDeniedError
from domain.interfaces.chat_session_repository import ChatSessionRepositoryInterface
from domain.interfaces.chat_message_repository import ChatMessageRepositoryInterface
from domain.interfaces.llm_provider import LLMProviderInterface

logger = logging.getLogger(__name__)


class ChatService:
    """
    Orchestrates chat sessions, message persistence, and LLM interactions.

    For each user message:
    1. Persist the user message.
    2. Run TWO concurrent LLM calls:
       a. Conversational reply (using full history).
       b. Grammar/style feedback analysis (using only the user message).
    3. Persist the assistant reply and the feedback.
    4. Touch the session's updated_at timestamp.
    """

    def __init__(
        self,
        session_repo: ChatSessionRepositoryInterface,
        message_repo: ChatMessageRepositoryInterface,
        llm: LLMProviderInterface,
    ) -> None:
        self._session_repo = session_repo
        self._message_repo = message_repo
        self._llm = llm

    # -------------------------------------------------------------------------
    # Session management
    # -------------------------------------------------------------------------

    async def create_session(self, user_id: UUID, topic: str | None) -> ChatSessionModel:
        return await self._session_repo.create(user_id=user_id, topic=topic)

    async def list_sessions(
        self, user_id: UUID, skip: int = 0, limit: int = 50
    ) -> list[ChatSessionModel]:
        return await self._session_repo.list_by_user(user_id, skip=skip, limit=limit)

    async def get_session(
        self, user_id: UUID, session_id: UUID
    ) -> tuple[ChatSessionModel, list[ChatMessageModel]]:
        session = await self._session_repo.get_by_id(session_id)
        if session is None:
            raise ChatSessionNotFoundError(str(session_id))
        if session.user_id != user_id:
            raise ChatSessionAccessDeniedError(str(session_id))

        messages = await self._message_repo.list_by_session(session_id)
        return session, messages

    async def delete_session(self, user_id: UUID, session_id: UUID) -> None:
        session = await self._session_repo.get_by_id(session_id)
        if session is None:
            raise ChatSessionNotFoundError(str(session_id))
        if session.user_id != user_id:
            raise ChatSessionAccessDeniedError(str(session_id))
        await self._session_repo.delete(session_id)

    # -------------------------------------------------------------------------
    # Sending a message
    # -------------------------------------------------------------------------

    async def send_message(
        self,
        user_id: UUID,
        session_id: UUID,
        content: str,
    ) -> tuple[ChatMessageModel, MessageFeedbackModel]:
        """
        Process a user message:
        - Validates session ownership.
        - Persists user message.
        - Fires two parallel LLM calls (reply + feedback).
        - Persists assistant reply and feedback.
        - Returns (assistant_message, feedback).
        """
        session = await self._session_repo.get_by_id(session_id)
        if session is None:
            raise ChatSessionNotFoundError(str(session_id))
        if session.user_id != user_id:
            raise ChatSessionAccessDeniedError(str(session_id))

        history = await self._message_repo.list_by_session(session_id)

        user_msg = await self._message_repo.create_message(
            session_id=session_id, role="user", content=content
        )

        reply_text, feedback_model = await asyncio.gather(
            self._llm.get_chat_reply(history=history, user_message=content),
            self._llm.analyze_message(user_message=content),
        )

        assistant_msg = await self._message_repo.create_message(
            session_id=session_id, role="assistant", content=reply_text
        )

        corrections_json = json.dumps(
            [{"original": c.original, "issue": c.issue, "suggestion": c.suggestion}
             for c in feedback_model.corrections]
        )
        recommendations_json = json.dumps(
            [{"original": r.original, "better_expression": r.better_expression, "reason": r.reason}
             for r in feedback_model.recommendations]
        )
        persisted_feedback = await self._message_repo.create_feedback(
            message_id=user_msg.id,
            corrections_json=corrections_json,
            recommendations_json=recommendations_json,
        )

        await self._session_repo.touch(session_id)

        return assistant_msg, persisted_feedback
