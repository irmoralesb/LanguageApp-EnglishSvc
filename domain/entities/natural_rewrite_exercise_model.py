from dataclasses import dataclass
import datetime
from uuid import UUID


@dataclass
class NaturalRewriteExercisePrompt:
    target_language_code: str
    scenario_native: str
    stiff_sentence: str
    context_note: str


@dataclass
class NaturalRewriteEvaluation:
    is_correct: bool
    feedback: str
    model_answer: str | None = None


@dataclass
class NaturalRewriteHistoryRecord:
    id: UUID | None
    user_id: UUID
    target_language_code: str
    scenario_native: str
    stiff_sentence: str
    user_answer: str
    is_correct: bool
    feedback: str
    model_answer: str
    created_at: datetime.datetime | None = None
