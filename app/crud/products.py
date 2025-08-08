"""Модуль для создания CRUD операций для продукта."""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import AbstractCRUDBase
from app.models import Category, Product


class CRUDProduct(AbstractCRUDBase):
    """Класс для создания CRUD операций для продукта."""

    async def get_products_by_category_or_is_active_or_all(
        self,
        category_slug: str | None,
        is_active: bool,
        session: AsyncSession
    ) -> list[Product]:
        """
        Метод для получения всех продуктов по категории и наличии товара.

        Если у категории есть подкатегории, то их продукты тоже будут включены.
        """
        query = select(Product)
        if category_slug:
            query = (query.
                     join(Category, Category.slug == Product.category_slug).
                     where(or_(Product.category_slug == category_slug,
                               Category.parent_slug == category_slug)))
        if is_active:
            query = query.where(Product.is_active == is_active)
        products = await session.execute(query)
        return products.scalars().all()


product_crud = CRUDProduct(Product)
