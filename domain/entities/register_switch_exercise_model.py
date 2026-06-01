from dataclasses import dataclass
import datetime
from uuid import UUID


@dataclass
class RegisterSwitchExercisePrompt:
    target_language_code: str
    scenario_native: str
    source_sentence: str
    source_register: str
    target_register: str
    slang_level: str | None


@dataclass
class RegisterSwitchEvaluation:
    is_correct: bool
    feedback: str
    model_answer: str | None = None


@dataclass
class RegisterSwitchHistoryRecord:
    id: UUID | None
    user_id: UUID
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
    created_at: datetime.datetime | None = None
