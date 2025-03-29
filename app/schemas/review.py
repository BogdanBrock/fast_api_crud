"""Модуль для создания схем."""

from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator

from app.models import Review


class ReviewSchema(BaseModel):
    """Схема ReviewSchema для валидации данных."""

    text: str | None = None
    grade: int

    @field_validator('grade', mode='after')
    @classmethod
    def grade_validate(cls, value):
        if not (0 <= value <= 10):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Оценка должна быть от '
                                       '0 и до 10 включительно.')
        return value

