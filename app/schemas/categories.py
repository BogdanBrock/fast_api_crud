"""Модуль для создания схем модели Category."""

from pydantic import BaseModel, Field

from app.core.constants import CATEGORY_NAME_MAX_LENGTH
from app.schemas.mixins import SlugMixin


class CategoryUpdateSchema(BaseModel, SlugMixin):
    """Схема для валидации и обновления данных."""

    name: str = Field(max_length=CATEGORY_NAME_MAX_LENGTH, default=None)


class CategoryCreateSchema(BaseModel, SlugMixin):
    """Схема для валидации и создания данных."""

    name: str = Field(max_length=CATEGORY_NAME_MAX_LENGTH)
    parent_slug: str | None = None


class CategoryReadSchema(BaseModel):
    """Схема для чтения данных."""

    id: int
    name: str
    slug: str
    parent_slug: str | None
