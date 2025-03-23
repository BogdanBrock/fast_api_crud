from pydantic import BaseModel, Field

from app.core.constants import REVIEW_TEXT_MAX_LENGTH


class ReviewSchema(BaseModel):
    text: str | None = Field(max_length=REVIEW_TEXT_MAX_LENGTH, default=None)
    grade: int = Field(ge=0, le=10)
