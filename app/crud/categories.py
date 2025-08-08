"""Модуль для создания CRUD операций для категории."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import AbstractCRUDBase
from app.models import Category


class CRUDCategory(AbstractCRUDBase):
    """Класс для создания CRUD операций для категории."""

    async def get_subcategories_by_category_or_all(
        self,
        parent_slug: str,
        session: AsyncSession,
    ) -> list[Category]:
        """
        Метод для получения всех категорий.

        Так же можно отсортировать категории по родительской категории.
        """
        query = select(Category)
        if parent_slug:
            query = query.where(Category.parent_slug == parent_slug)
        categories = await session.execute(query)
        return categories.scalars().all()

    async def get_parent_slug(
        self,
        parent_slug: str,
        session: AsyncSession
    ) -> str:
        """Метод для получения существующего поля parent_slug."""
        category = await session.execute(
            select(Category.parent_slug).
            where(Category.parent_slug == parent_slug)
        )
        return category.scalar()


category_crud = CRUDCategory(Category)
