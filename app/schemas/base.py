"""Модуль для создания миксинов."""

from slugify import slugify
from pydantic import BaseModel, computed_field


class AbstractBaseModel(BaseModel):
    """Абстрактный класс для наследования."""

    @computed_field
    def slug(self) -> str:
        """Функция для вычисления поля slug."""
        return slugify(self.name)
