"""Модуль для создания схем."""

from pydantic import BaseModel, Field


class ReviewSchema(BaseModel):
    """Схема ReviewSchema для валидации данных."""

    text: str | None = None
    grade: int = Field(ge=0, le=10)
