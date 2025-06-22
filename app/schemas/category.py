"""Модуль для создания схем модели Category."""

from pydantic import BaseModel, Field, computed_field
from slugify import slugify

from app.core.constants import CATEGORY_NAME_MAX_LENGTH
from app.schemas import AbstractCreateSchema, AbstractUpdateSchema


class CategoryUpdateSchema(AbstractUpdateSchema):
    """Схема CategoryUpdateSchema для валидации и обновления данных."""

    name: str = Field(max_length=CATEGORY_NAME_MAX_LENGTH, default=None)


class CategoryCreateSchema(AbstractCreateSchema):
    """Схема CategoryCreateSchema для валидации и создания данных."""

    name: str = Field(max_length=CATEGORY_NAME_MAX_LENGTH)
    parent_slug: str | None = None


class CategoryReadSchema(BaseModel):
    """Схема CategoryReadSchema для чтения данных."""

    id: int
    name: str
    slug: str
    parent_slug: str | None
