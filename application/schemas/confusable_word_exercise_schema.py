from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ConfusableWordExerciseRequest(BaseModel):
    target_language_code: str = Field(min_length=2, max_length=10)


class ConfusableWordExercisePromptResponse(BaseModel):
    option_a: str
    option_b: str
    target_language_code: str
    scenario_native: str
    sentence_with_blank: str
    prompt_token: str


class ConfusableWordAnswerRequest(BaseModel):
    prompt_token: str = Field(min_length=1)
    user_answer: str = Field(min_length=1)


class ConfusableWordEvaluationResponse(BaseModel):
    is_correct: bool
    feedback: str
    correct_word: str | None = None
    sentence_complete: str | None = None


class ConfusableWordHistoryResponse(BaseModel):
    id: UUID
    option_a: str
    option_b: str
    target_language_code: str
    scenario_native: str
    sentence_with_blank: str
    sentence_complete: str
    correct_word: str
    user_answer: str
    is_correct: bool
    feedback: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConfusableWordPairStatsResponse(BaseModel):
    option_a: str
    option_b: str
    correct_count: int
    incorrect_count: int
