from dataclasses import dataclass
from uuid import UUID
import datetime


@dataclass
class PracticeTermModel:
    id: UUID | None
    term: str
    term_type: str
    definition: str
    example_sentence: str | None = None
    is_catalog: bool = True
    created_by_user_id: UUID | None = None
    created_at: datetime.datetime | None = None
