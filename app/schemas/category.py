"""Модуль для создания схем."""

from pydantic import BaseModel, Field

from .mixins import SlugMixin
from app.core.constants import CATEGORY_NAME_MAX_LENGTH


class CategorySchema(BaseModel, SlugMixin):
    """Схема CategorySchema для валидации данных."""

    name: str = Field(max_length=CATEGORY_NAME_MAX_LENGTH)
    parent_id: int | None = None
