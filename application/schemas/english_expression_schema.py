from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class EnglishExpressionCreate(BaseModel):
    text: str = Field(min_length=1, max_length=200)
    expression_type: str = Field(min_length=1, max_length=30)
    definition: str = Field(min_length=1, max_length=500)
    example_sentence: str | None = Field(default=None, max_length=1000)
    register: str = Field(default="neutral", max_length=20)


class EnglishExpressionUpdate(BaseModel):
    text: str = Field(min_length=1, max_length=200)
    expression_type: str = Field(min_length=1, max_length=30)
    definition: str = Field(min_length=1, max_length=500)
    example_sentence: str | None = Field(default=None, max_length=1000)
    register: str = Field(default="neutral", max_length=20)


class EnglishExpressionResponse(BaseModel):
    id: UUID
    text: str
    expression_type: str
    definition: str
    example_sentence: str | None
    register: str
    is_catalog: bool
    created_by_user_id: UUID | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
