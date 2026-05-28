from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from typing import Optional

from domain.entities.message_feedback_model import MessageFeedbackModel


@dataclass
class ChatMessageModel:
    """Domain model for a single chat message."""
    id: UUID
    session_id: UUID
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime
    feedback: Optional[MessageFeedbackModel] = field(default=None)
