"""Модуль для создания схем модели Category."""

from pydantic import BaseModel, Field

from app.core.constants import CATEGORY_NAME_MAX_LENGTH
from app.schemas import AbstractBaseSchema


class CategoryUpdateSchema(AbstractBaseSchema):
    """Схема CategoryUpdateSchema для валидации и обновления данных."""

    name: str = Field(max_length=CATEGORY_NAME_MAX_LENGTH)


class CategoryCreateSchema(CategoryUpdateSchema):
    """Схема CategoryCreateSchema для валидации и создания данных."""

    parent_slug: str | None = None


class CategoryReadSchema(BaseModel):
    """Схема CategoryReadSchema для чтения данных."""

    id: int
    name: str
    slug: str
    parent_slug: str | None
