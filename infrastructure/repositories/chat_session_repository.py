import uuid
from datetime import datetime, timezone

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.chat_session_model import ChatSessionModel
from domain.interfaces.chat_session_repository import ChatSessionRepositoryInterface
from infrastructure.databases.models import ChatSessionDataModel


class ChatSessionRepository(ChatSessionRepositoryInterface):

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    def _to_model(self, row: ChatSessionDataModel) -> ChatSessionModel:
        return ChatSessionModel(
            id=row.id,
            user_id=row.user_id,
            topic=row.topic,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def create(self, user_id: uuid.UUID, topic: str | None) -> ChatSessionModel:
        row = ChatSessionDataModel(
            id=uuid.uuid4(),
            user_id=user_id,
            topic=topic,
        )
        self._db.add(row)
        await self._db.flush()
        await self._db.refresh(row)
        return self._to_model(row)

    async def get_by_id(self, session_id: uuid.UUID) -> ChatSessionModel | None:
        result = await self._db.execute(
            select(ChatSessionDataModel).where(ChatSessionDataModel.id == session_id)
        )
        row = result.scalar_one_or_none()
        return self._to_model(row) if row else None

    async def list_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[ChatSessionModel]:
        result = await self._db.execute(
            select(ChatSessionDataModel)
            .where(ChatSessionDataModel.user_id == user_id)
            .order_by(ChatSessionDataModel.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        rows = result.scalars().all()
        return [self._to_model(r) for r in rows]

    async def delete(self, session_id: uuid.UUID) -> None:
        await self._db.execute(
            delete(ChatSessionDataModel).where(ChatSessionDataModel.id == session_id)
        )

    async def touch(self, session_id: uuid.UUID) -> None:
        await self._db.execute(
            update(ChatSessionDataModel)
            .where(ChatSessionDataModel.id == session_id)
            .values(updated_at=datetime.now(timezone.utc))
        )
