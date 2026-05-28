from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

class CorrectionItemResponse(BaseModel):
    original: str
    issue: str
    suggestion: str


class RecommendationItemResponse(BaseModel):
    original: str
    better_expression: str
    reason: str


class MessageFeedbackResponse(BaseModel):
    id: UUID
    message_id: UUID
    corrections: list[CorrectionItemResponse]
    recommendations: list[RecommendationItemResponse]
    created_at: datetime


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

class ChatMessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime
    feedback: Optional[MessageFeedbackResponse] = None


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

class CreateSessionRequest(BaseModel):
    topic: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional topic or context for this chat session.",
    )


class ChatSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    topic: Optional[str]
    created_at: datetime
    updated_at: datetime


class ChatSessionDetailResponse(BaseModel):
    id: UUID
    user_id: UUID
    topic: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageResponse]


# ---------------------------------------------------------------------------
# Sending a message
# ---------------------------------------------------------------------------

class SendMessageRequest(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=4000,
        description="The user's message content.",
    )


class SendMessageResponse(BaseModel):
    assistant_message: ChatMessageResponse
    feedback: MessageFeedbackResponse
