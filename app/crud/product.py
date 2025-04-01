"""Модуль для создания CRUD операций для продукта."""

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import AbstractCRUDBase
from app.models import Product, Category


class CRUDProduct(AbstractCRUDBase):
    """Класс для созданий CRUD операций для продукта."""

    async def get_products_by_category_or_all(
        self,
        category_slug: str,
        session: AsyncSession
    ) -> list[Product]:
        """Метод для получения всех продуктов по категории."""
        query = select(Product)
        if category_slug:
            query = (query.
                     join(Category, Category.slug == Product.category_slug).
                     where(or_(Product.category_slug == category_slug,
                               Category.parent_slug == category_slug)))

        products = await session.execute(query)
        return products.scalars().all()


product_crud = CRUDProduct(Product)
