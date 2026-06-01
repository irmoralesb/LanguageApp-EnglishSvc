from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ExpressionMcGenerateRequest(BaseModel):
    english_expression_id: UUID | None = None


class IdiomCompletePromptResponse(BaseModel):
    english_expression_id: UUID
    text: str
    definition: str
    sentence_with_blank: str
    options: list[str]
    scenario_native: str
    prompt_token: str


class CollocationChoicePromptResponse(BaseModel):
    english_expression_id: UUID
    text: str
    definition: str
    sentence_with_blank: str
    options: list[str]
    scenario_native: str
    prompt_token: str


class ExpressionMcAnswerRequest(BaseModel):
    prompt_token: str = Field(min_length=1)
    user_answer: str = Field(min_length=1)


class ExpressionExerciseEvaluationResponse(BaseModel):
    is_correct: bool
    feedback: str
    correct_example: str | None = None


class UseInContextGenerateRequest(BaseModel):
    target_language_code: str = Field(min_length=2, max_length=10)
    english_expression_id: UUID | None = None


class UseInContextPromptResponse(BaseModel):
    english_expression_id: UUID
    text: str
    expression_type: str
    definition: str
    target_language_code: str
    scenario_native: str
    prompt_native: str
    expected_answer: str


class UseInContextAnswerRequest(BaseModel):
    english_expression_id: UUID
    target_language_code: str = Field(min_length=2, max_length=10)
    scenario_native: str = Field(min_length=1)
    prompt_native: str = Field(min_length=1)
    expected_answer: str = Field(min_length=1)
    user_answer: str = Field(min_length=1)


class ExpressionExerciseHistoryResponse(BaseModel):
    id: UUID
    english_expression_id: UUID
    exercise_type: str
    target_language_code: str
    scenario_native: str
    prompt_native: str
    expected_answer: str
    user_answer: str
    is_correct: bool
    feedback: str
    created_at: datetime

    model_config = {"from_attributes": True}
