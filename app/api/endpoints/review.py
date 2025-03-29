"""Модуль для создания маршрутов."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.user import get_current_user
from app.core.db import db_session
from app.crud import review_crud, product_crud
from app.api.validators import (check_product_exists,
                                check_review_exists,
                                check_object_duplicate,
                                user_cant_create_review_own_product)
from app.api.permissions import check_permission_for_user
from app.models import User
from app.schemas.review import ReviewSchema

router = APIRouter()


@router.get('/reviews/')
async def get_reviews(
    product_slug: str = None,
    session: AsyncSession = Depends(db_session),
):
    """Маршрут для получения всех отзывов или отзывов по продукту."""
    if product_slug:
        return await review_crud.get_reviews_by_product(
            product_slug, session
        )
    return await review_crud.get_all(session)


@router.get('/reviews/{review_id}/')
async def get_review(
    review_id: int,
    session: AsyncSession = Depends(db_session),
):
    """Маршрут для получения отзыва."""
    review = await review_crud.get(review_id, session)
    await check_review_exists(review)
    return review


@router.post(
    '/products/{product_slug}/reviews/',
    status_code=status.HTTP_201_CREATED
)
async def create_review(
    product_slug: str,
    rating_schema: ReviewSchema,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_session),
):
    """Маршрут для создания отзыва."""
    product = await product_crud.get_product_by_slug_with_user(
        product_slug, session
    )
    await check_product_exists(product)
    review = await review_crud.get_review_by_product_id_and_user_id(
        product.id, user.id, session
    )
    await user_cant_create_review_own_product(user, product.user)
    await check_object_duplicate(review)
    return await review_crud.create(rating_schema, session, user)


@router.put('/products/{product_slug}/reviews/{review_id}/')
async def update_review(
    product_slug: str,
    review_id: int,
    review_schema: ReviewSchema,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_session)
):
    """Маршрут для изменения отзыва."""
    product = await product_crud.get_object_by_slug(product_slug, session)
    await check_product_exists(product)
    review = await review_crud.get_review_by_id_with_user(review_id, session)
    await check_review_exists(review)
    await check_permission_for_user(user, review.user)
    return await review_crud.update(review, review_schema, session)


@router.delete(
    '/products/{product_slug}/reviews/{review_id}/',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_review(
    product_slug: str,
    review_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_session),
) -> None:
    """Маршрут для удаления отзыва."""
    product = await product_crud.get_object_by_slug(product_slug, session)
    await check_product_exists(product)
    review = await review_crud.get_review_by_id_with_user(review_id, session)
    await check_review_exists(review)
    await check_permission_for_user(user, review.user)
    await review_crud.delete(review, session)
