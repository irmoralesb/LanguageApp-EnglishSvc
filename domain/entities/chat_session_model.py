from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ChatSessionModel:
    """Domain model for a chat session."""
    id: UUID
    user_id: UUID
    topic: str | None
    created_at: datetime
    updated_at: datetime
