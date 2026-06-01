from dataclasses import dataclass
import datetime
from uuid import UUID


@dataclass
class IdiomCompleteExercisePrompt:
    english_expression_id: UUID
    text: str
    definition: str
    sentence_with_blank: str
    options: list[str]
    scenario_native: str


@dataclass
class CollocationChoiceExercisePrompt:
    english_expression_id: UUID
    text: str
    definition: str
    sentence_with_blank: str
    options: list[str]
    scenario_native: str


@dataclass
class ExpressionWritingPrompt:
    english_expression_id: UUID
    text: str
    expression_type: str
    definition: str
    target_language_code: str
    scenario_native: str
    prompt_native: str
    expected_answer: str


@dataclass
class ExpressionExerciseEvaluation:
    is_correct: bool
    feedback: str
    correct_example: str | None = None


@dataclass
class ExpressionExerciseHistoryRecord:
    id: UUID | None
    user_id: UUID
    english_expression_id: UUID
    exercise_type: str
    target_language_code: str
    scenario_native: str
    prompt_native: str
    expected_answer: str
    user_answer: str
    is_correct: bool
    feedback: str
    created_at: datetime.datetime | None = None
