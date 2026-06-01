from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class NaturalRewriteExerciseRequest(BaseModel):
    target_language_code: str = Field(min_length=2, max_length=10)


class NaturalRewriteExercisePromptResponse(BaseModel):
    target_language_code: str
    scenario_native: str
    stiff_sentence: str
    context_note: str
    prompt_token: str


class NaturalRewriteAnswerRequest(BaseModel):
    prompt_token: str = Field(min_length=1)
    user_answer: str = Field(min_length=1)


class NaturalRewriteEvaluationResponse(BaseModel):
    is_correct: bool
    feedback: str
    model_answer: str | None = None


class NaturalRewriteHistoryResponse(BaseModel):
    id: UUID
    target_language_code: str
    scenario_native: str
    stiff_sentence: str
    user_answer: str
    is_correct: bool
    feedback: str
    model_answer: str
    created_at: datetime

    model_config = {"from_attributes": True}
