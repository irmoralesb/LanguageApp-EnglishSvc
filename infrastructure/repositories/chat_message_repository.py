import json
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.entities.chat_message_model import ChatMessageModel
from domain.entities.message_feedback_model import (
    MessageFeedbackModel,
    CorrectionItem,
    RecommendationItem,
)
from domain.interfaces.chat_message_repository import ChatMessageRepositoryInterface
from infrastructure.databases.models import ChatMessageDataModel, MessageFeedbackDataModel


class ChatMessageRepository(ChatMessageRepositoryInterface):

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    def _feedback_from_row(
        self, row: MessageFeedbackDataModel, message_id: uuid.UUID
    ) -> MessageFeedbackModel:
        corrections = [
            CorrectionItem(**c) for c in json.loads(row.corrections or "[]")
        ]
        recommendations = [
            RecommendationItem(**r) for r in json.loads(row.recommendations or "[]")
        ]
        return MessageFeedbackModel(
            id=row.id,
            message_id=message_id,
            corrections=corrections,
            recommendations=recommendations,
            created_at=row.created_at,
        )

    def _message_from_row(self, row: ChatMessageDataModel) -> ChatMessageModel:
        feedback = None
        if row.feedback:
            feedback = self._feedback_from_row(row.feedback, row.id)
        return ChatMessageModel(
            id=row.id,
            session_id=row.session_id,
            role=row.role,
            content=row.content,
            created_at=row.created_at,
            feedback=feedback,
        )

    async def create_message(
        self, session_id: uuid.UUID, role: str, content: str
    ) -> ChatMessageModel:
        row = ChatMessageDataModel(
            id=uuid.uuid4(),
            session_id=session_id,
            role=role,
            content=content,
        )
        self._db.add(row)
        await self._db.flush()
        await self._db.refresh(row)
        return self._message_from_row(row)

    async def create_feedback(
        self,
        message_id: uuid.UUID,
        corrections_json: str,
        recommendations_json: str,
    ) -> MessageFeedbackModel:
        row = MessageFeedbackDataModel(
            id=uuid.uuid4(),
            message_id=message_id,
            corrections=corrections_json,
            recommendations=recommendations_json,
        )
        self._db.add(row)
        await self._db.flush()
        await self._db.refresh(row)
        return self._feedback_from_row(row, message_id)

    async def list_by_session(self, session_id: uuid.UUID) -> list[ChatMessageModel]:
        result = await self._db.execute(
            select(ChatMessageDataModel)
            .where(ChatMessageDataModel.session_id == session_id)
            .options(selectinload(ChatMessageDataModel.feedback))
            .order_by(ChatMessageDataModel.created_at.asc())
        )
        rows = result.scalars().all()
        return [self._message_from_row(r) for r in rows]
