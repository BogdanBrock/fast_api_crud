"""Модуль для создания схем."""

from pydantic import Field

from .base import AbstractBaseModel
from app.core.constants import CATEGORY_NAME_MAX_LENGTH


class CategorySchema(AbstractBaseModel):
    """Схема CategorySchema для валидации данных."""

    name: str = Field(max_length=CATEGORY_NAME_MAX_LENGTH)
    parent_id: int | None = None
