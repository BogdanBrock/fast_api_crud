"""Модуль для создания миксинов."""

from slugify import slugify
from pydantic import computed_field


class SlugMixin:
    """Миксин SlugMixin."""

    @computed_field
    def slug(self) -> str:
        """Функция для вычисления поля slug."""
        return slugify(self.name)
