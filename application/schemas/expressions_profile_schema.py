from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AddEnglishExpressionSelection(BaseModel):
    english_expression_id: UUID


class EnglishExpressionSelectionResponse(BaseModel):
    id: UUID
    user_id: UUID
    english_expression_id: UUID
    added_at: datetime | None = None

    model_config = {"from_attributes": True}
