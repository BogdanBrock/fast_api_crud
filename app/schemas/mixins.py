"""Модуль для миксинов."""

from pydantic import computed_field
from slugify import slugify


class SlugMixin:
    """Миксин для подмешивания slug."""

    @computed_field
    def slug(self) -> str:
        """Функция для вычисления slug по имени."""
        return slugify(self.name) if self.name else None
