from dataclasses import dataclass
import datetime
from uuid import UUID


@dataclass
class ConfusableWordExercisePrompt:
    option_a: str
    option_b: str
    target_language_code: str
    scenario_native: str
    sentence_with_blank: str
    correct_word: str
    sentence_complete: str


@dataclass
class ConfusableWordEvaluation:
    is_correct: bool
    feedback: str
    correct_word: str | None = None
    sentence_complete: str | None = None


@dataclass
class ConfusableWordHistoryRecord:
    id: UUID | None
    user_id: UUID
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
    created_at: datetime.datetime | None = None


@dataclass
class ConfusableWordPairStats:
    option_a: str
    option_b: str
    correct_count: int
    incorrect_count: int
