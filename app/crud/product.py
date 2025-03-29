"""Модуль для создания CRUD операций для продукта."""

from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import AbstractCRUDBase
from app.models import Product, Category


class CRUDProduct(AbstractCRUDBase):
    """Класс для созданий CRUD операций для продукта."""

    async def get_products_by_category(
        self,
        category_slug: str,
        session: AsyncSession
    ) -> list[Product]:
        """Метод для получения всех продуктов по категории."""
        category_id = (
            select(Category.id).
            where(Category.slug == category_slug).
            scalar_subquery()
        )
        products = await session.execute(
            select(Product).
            join(Category, Category.id == Product.category_id).
            where(or_(Product.category_id == category_id,
                      Category.parent_id == category_id))
        )
        return products.scalars().all()

    async def get_product_by_slug_with_user(
        self,
        product_slug,
        session: AsyncSession
    ) -> Product | None:
        """Метод для получения продукта по slug с пользователем."""
        review = await session.execute(
            select(Product).
            options(joinedload(Product.user)).
            where(Product.slug == product_slug)
        )
        return review.scalar()


product_crud = CRUDProduct(Product)
