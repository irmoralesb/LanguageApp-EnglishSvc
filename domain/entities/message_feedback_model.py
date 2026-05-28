from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class CorrectionItem:
    """A single grammar/spelling/style correction."""
    original: str
    issue: str
    suggestion: str


@dataclass
class RecommendationItem:
    """A vocabulary/expression recommendation."""
    original: str
    better_expression: str
    reason: str


@dataclass
class MessageFeedbackModel:
    """Domain model for feedback attached to a user message."""
    id: UUID
    message_id: UUID
    corrections: list[CorrectionItem] = field(default_factory=list)
    recommendations: list[RecommendationItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
