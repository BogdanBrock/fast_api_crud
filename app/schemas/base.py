"""Модуль для абстрактных классов."""

from slugify import slugify
from pydantic import BaseModel, computed_field


class AbstractBaseSchema(BaseModel):
    """Абстрактный класс для наследования."""

    @computed_field
    def slug(self) -> str | None:
        """Функция для вычисления slug по имени."""
        return slugify(self.name) if self.name else None
