"""Модуль для абстрактных классов."""

from pydantic import BaseModel, computed_field
from slugify import slugify


class AbstractCreateSchema(BaseModel):
    """Абстрактный класс для создания."""

    @computed_field
    def slug(self) -> str:
        """Функция для вычисления slug по имени."""
        return slugify(self.name)


class AbstractUpdateSchema(BaseModel):
    """Абстрактный класс для обновления"""

    def model_dump(self, *args, **kwargs):
        """Метод для создания словаря из модели pydantic."""
        data = super().model_dump(*args, **kwargs)
        name = data.get('name')
        if name:
            data['slug'] = slugify(name)
        return data
