"""Модуль для создания CRUD операций для категории."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import AbstractCRUDBase
from app.models import Category


class CRUDCategory(AbstractCRUDBase):
    """Класс для созданий CRUD операций для категории."""

    async def get_subcategories_by_category(
        self,
        category_slug: str,
        session: AsyncSession,
    ) -> list[Category]:
        """Метод для получения всех подкатегорий по категории."""
        parent_id = (
            select(Category.id).
            where(Category.slug == category_slug).
            scalar_subquery()
        )
        subcategories = await session.execute(
            select(Category).
            where(Category.parent_id == parent_id)
        )
        return subcategories.scalars().all()


category_crud = CRUDCategory(Category)
