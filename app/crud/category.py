"""Модуль для создания CRUD операций для категории."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import AbstractCRUDBase
from app.models import Category


class CRUDCategory(AbstractCRUDBase):
    """Класс для созданий CRUD операций для категории."""

    async def get_subcategories_by_category_or_all(
        self,
        parent_slug: str,
        session: AsyncSession,
    ) -> list[Category]:
        """Метод для получения всех подкатегорий по категории."""
        query = select(Category)
        if parent_slug:
            query = query.where(Category.parent_slug == parent_slug)
        categories = await session.execute(query)
        return categories.scalars().all()


category_crud = CRUDCategory(Category)
