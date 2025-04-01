"""Модуль для создания CRUD операций для отзыва."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Review


class CRUDReview(CRUDBase):
    """Класс для созданий CRUD операций для отзыва."""

    async def get_reviews_by_product_or_all(
        self,
        product_slug: str,
        session: AsyncSession
    ) -> list[Review]:
        """Метод для получения всех отзывов по продукту."""
        query = select(Review)
        if product_slug:
            query = query.where(Review.product_slug == product_slug)
        reviews = await session.execute(query)
        return reviews.scalars().all()

    async def get_review_by_product_slug_and_username(
        self,
        product_slug,
        username,
        session: AsyncSession
    ) -> Review | None:
        """Метод для получения отзыва по slug продукта и имени пользователю."""
        review = await session.execute(
            select(Review).
            where(Review.product_slug == product_slug,
                  Review.user_username == username)
        )
        return review.scalar()


review_crud = CRUDReview(Review)
