"""Модуль для абстрактных классов."""

from pydantic import BaseModel, computed_field
from slugify import slugify


class AbstractBaseSchema(BaseModel):
    """Абстрактный класс для наследования."""

    def model_dump(self, *args, **kwargs):
        """Метод для создания словаря из модели pydantic."""
        data = super().model_dump(*args, **kwargs)
        data['slug'] = slugify(data['name'])
        return data

    @computed_field
    def slug(self) -> str | None:
        """Функция для вычисления slug по имени."""
        return slugify(self.name) if self.name else None
