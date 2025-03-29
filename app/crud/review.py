"""Модуль для создания CRUD операций для отзыва."""

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Product, Review


class CRUDReview(CRUDBase):
    """Класс для созданий CRUD операций для отзыва."""

    async def get_reviews_by_product(
        self,
        product_slug: str,
        session: AsyncSession
    ) -> list[Review]:
        """Метод для получения всех отзывов по продукту."""
        product_id = (
            select(Product.id).
            where(Product.slug == product_slug).
            scalar_subquery()
        )
        reviews = await session.execute(
            select(Review).
            where(Review.product_id == product_id)
        )
        return reviews.scalars().all()

    async def get_review_by_product_id_and_user_id(
        self,
        product_id,
        user_id,
        session: AsyncSession
    ) -> Review | None:
        """Метод для получения отзыва по id продукта и пользователя."""
        review = await session.execute(
            select(Review).
            where(Review.product_id == product_id,
                  Review.user_id == user_id)
        )
        return review.scalar()

    async def get_review_by_id_with_user(
        self,
        review_id,
        session: AsyncSession
    ) -> Review | None:
        """Метод для получения отзыва по id с пользователем."""
        review = await session.execute(
            select(Review).
            options(joinedload(Review.user)).
            where(Review.id == review_id)
        )
        return review.scalar()


review_crud = CRUDReview(Review)
