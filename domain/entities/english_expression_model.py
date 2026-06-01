from dataclasses import dataclass
from uuid import UUID
import datetime


EXPRESSION_TYPES = ("idiom", "collocation", "proverb")
REGISTERS = ("formal", "neutral", "casual")


@dataclass
class EnglishExpressionModel:
    id: UUID | None
    text: str
    expression_type: str
    definition: str
    example_sentence: str | None
    register: str
    is_catalog: bool = True
    created_by_user_id: UUID | None = None
    created_at: datetime.datetime | None = None
