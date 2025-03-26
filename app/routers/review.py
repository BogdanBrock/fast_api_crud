"""Модуль для создания маршрутов."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Body, Query, status
from sqlalchemy import select, insert, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import const
from app.core.db import get_db
from app.core.exceptions import NotFound
from app.core.permissions import has_object_permission
from app.models import Review, Product, User
from app.schemas.review import ReviewSchema
from app.routers.auth import get_current_user

router = APIRouter(tags=['Reviews'])


@router.get('/reviews/')
async def get_reviews(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_slug: Annotated[str, Query()] = None
):
    """Маршрут для получения всех отзывов или отзывов по продукту."""
    if product_slug:
        product = await session.scalar(
            select(Product).
            options(joinedload(Product.reviews).
                    load_only(*const.REVIEW_FIELDS)).
            where(Product.slug == product_slug)
        )
        return [] if not product else product.reviews
    reviews = await session.execute(select(*const.REVIEW_FIELDS))
    return reviews.mappings().all()


@router.get('/reviews/{review_id}/')
async def get_review(
    session: Annotated[AsyncSession, Depends(get_db)],
    review_id: Annotated[int, Path()]
):
    """Маршрут для получения отзыва."""
    review = await session.execute(
        select(*const.REVIEW_FIELDS).
        where(Review.id == review_id)
    )
    if review := review.mappings().first():
        return review
    raise NotFound('Такого отзыва не существует.')


@router.post('/products/{product_slug}/reviews/',
             status_code=status.HTTP_201_CREATED)
async def create_review(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    rating_schema: Annotated[ReviewSchema, Body()],
    product_slug: Annotated[str, Path()]
):
    """Маршрут для создания отзыва."""
    product = await session.scalar(
        select(Product).
        options(joinedload(Product.user).load_only(User.username)).
        where(Product.slug == product_slug)
    )
    if not product:
        raise NotFound('Такого продукта не существует.')
    # ReviewSchema.validate_owner_cant_rate_own_product(product, user)
    review_fields = rating_schema.model_dump()
    review_fields.update({'user_id': user.get('id'),
                          'product_id': product.id})
    review = await session.execute(
        insert(Review).
        values(**review_fields).
        returning(*const.REVIEW_FIELDS)
    )
    await session.commit()
    return review.mappings().first()


@router.put('/products/{product_slug}/reviews/{review_id}/')
async def update_review(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    review_schema: Annotated[ReviewSchema, Body()],
    product_slug: Annotated[str, Path()],
    review_id: Annotated[int, Path()]
):
    """Маршрут для изменения отзыва."""
    product = await session.scalar(
        select(Product).
        where(Product.slug == product_slug)
    )
    if not product:
        raise NotFound('Такого продукта не существует.')
    review = await session.scalar(
        select(Review).
        options(joinedload(Review.user)).
        where(Review.id == review_id)
    )
    if not review:
        raise NotFound('Такого отзыва не существует.')
    has_object_permission(user, review)
    review_updated = await session.execute(
        update(Review).
        where(Review.id == review_id).
        values(**review_schema.model_dump()).
        returning(*const.REVIEW_FIELDS)
    )
    await session.commit()
    return review_updated.mappings().first()


@router.delete('/products/{product_slug}/reviews/{review_id}/',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    product_slug: Annotated[str, Path()],
    review_id: Annotated[int, Path()]
):
    """Маршрут для удаления отзыва."""
    product = await session.scalar(
        select(Product).
        where(Product.slug == product_slug)
    )
    if not product:
        raise NotFound('Такого продукта не существует.')
    review = await session.scalar(
        select(Review).
        options(joinedload(Review.user)).
        where(Review.id == review_id)
    )
    if not review:
        raise NotFound('Такого отзыва не существует.')
    has_object_permission(user, review)
    await session.delete(review)
    await session.commit()
