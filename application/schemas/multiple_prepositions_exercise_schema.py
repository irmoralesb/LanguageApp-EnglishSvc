from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class MultiplePrepositionsExerciseRequest(BaseModel):
    target_language_code: str = Field(min_length=2, max_length=10)


class MultiplePrepositionsExercisePromptResponse(BaseModel):
    """Response sent on /generate.

    NOTE: the reference translation (`sentence_target`) is intentionally NOT
    included here. It is round-tripped opaquely via `prompt_token`, an HMAC
    signed payload the client must echo on /evaluate. The server is the only
    party that can read or trust its contents.
    """
    practice_term_ids: list[UUID]
    practice_term_texts: list[str]
    target_language_code: str
    sentence_native: str
    prompt_token: str


class MultiplePrepositionsAnswerRequest(BaseModel):
    prompt_token: str = Field(min_length=1)
    user_answer: str = Field(min_length=1)
    attempt_number: int = Field(ge=1, le=2)


class PrepositionFeedbackItem(BaseModel):
    preposition: str
    used_correctly: bool
    explanation: str


class MultiplePrepositionsEvaluationResponse(BaseModel):
    is_correct: bool
    feedback: str
    preposition_feedback: list[PrepositionFeedbackItem] = Field(default_factory=list)
    minor_issues: list[str] = Field(default_factory=list)
    attempt_number: int
    correct_sentence_target: str | None = None


class MultiplePrepositionsHistoryResponse(BaseModel):
    id: UUID
    practice_term_ids: list[UUID]
    target_language_code: str
    sentence_native: str
    sentence_target: str
    user_answer: str
    attempt_number: int
    is_correct: bool
    feedback: str
    revealed: bool
    created_at: datetime

    model_config = {"from_attributes": True}
