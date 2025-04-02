"""Модуль для создания схем модели Review."""

from pydantic import BaseModel, Field


class ReviewUpdateSchema(BaseModel):
    """Схема ReviewUpdateSchema для валидации и обновления данных."""

    text: str | None = None
    grade: int = Field(ge=1, le=10, default=None)


class ReviewCreateSchema(ReviewUpdateSchema):
    """Схема ReviewCreateSchema для валидации и создания данных."""

    grade: int = Field(ge=1, le=10)


class ReviewReadSchema(BaseModel):
    """Схема ReviewReadSchema для чтения данных."""

    id: int
    text: str | None
    grade: int
    product_slug: str
    user_username: str
