from dataclasses import dataclass
import datetime
from uuid import UUID


@dataclass
class PrepositionChoiceExercisePrompt:
    """Generated exercise: English sentence with a blank for one preposition."""
    option_a: str
    option_b: str
    target_language_code: str
    scenario_native: str
    sentence_with_blank: str
    correct_preposition: str
    sentence_complete: str
    practice_term_id_a: UUID | None = None
    practice_term_id_b: UUID | None = None


@dataclass
class PrepositionChoiceEvaluation:
    is_correct: bool
    feedback: str
    correct_preposition: str | None = None
    sentence_complete: str | None = None


@dataclass
class PrepositionChoiceHistoryRecord:
    id: UUID | None
    user_id: UUID
    option_a: str
    option_b: str
    target_language_code: str
    scenario_native: str
    sentence_with_blank: str
    sentence_complete: str
    correct_preposition: str
    user_answer: str
    is_correct: bool
    feedback: str
    created_at: datetime.datetime | None = None


@dataclass
class PrepositionChoicePairStats:
    option_a: str
    option_b: str
    correct_count: int
    incorrect_count: int
