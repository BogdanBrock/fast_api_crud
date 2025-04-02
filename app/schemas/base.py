"""Модуль для абстрактных классов."""

from pydantic import BaseModel, computed_field
from slugify import slugify


class AbstractBaseSchema(BaseModel):
    """Абстрактный класс для наследования."""

    @computed_field
    def slug(self) -> str | None:
        """Функция для вычисления slug по имени."""
        return slugify(self.name) if self.name else None
