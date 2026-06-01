from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class RegisterSwitchExerciseRequest(BaseModel):
    target_language_code: str = Field(min_length=2, max_length=10)
    target_register: str | None = Field(default=None, max_length=20)
    slang_level: str | None = Field(default=None, max_length=20)


class RegisterSwitchExercisePromptResponse(BaseModel):
    target_language_code: str
    scenario_native: str
    source_sentence: str
    source_register: str
    target_register: str
    slang_level: str | None
    prompt_token: str


class RegisterSwitchAnswerRequest(BaseModel):
    prompt_token: str = Field(min_length=1)
    user_answer: str = Field(min_length=1)


class RegisterSwitchEvaluationResponse(BaseModel):
    is_correct: bool
    feedback: str
    model_answer: str | None = None


class RegisterSwitchHistoryResponse(BaseModel):
    id: UUID
    target_language_code: str
    scenario_native: str
    source_sentence: str
    source_register: str
    target_register: str
    slang_level: str | None
    user_answer: str
    is_correct: bool
    feedback: str
    model_answer: str
    created_at: datetime

    model_config = {"from_attributes": True}
