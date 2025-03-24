"""Модуль для создания маршрутов."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Body, Query, status
from sqlalchemy import select, insert, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.exceptions import get_object_or_404
from app.core.validators import (validate_owner,
                                 validate_owner_cant_rate_own_product)
from app.schemas.review import ReviewSchema
from app.models.review import Review
from app.models.product import Product
from app.models.user import User
from app.core.constants import const
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
            options(joinedload(Product.reviews).load_only(*const.REVIEW_FIELDS)).
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
    review = await get_object_or_404(
        select(*const.REVIEW_FIELDS).
        where(Review.id == review_id),
        session,
        get_mapping=True
    )
    return review


@router.post('/products/{product_slug}/reviews/',
             status_code=status.HTTP_201_CREATED)
async def create_review(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    rating_schema: Annotated[ReviewSchema, Body()],
    product_slug: Annotated[str, Path()]
):
    """Маршрут для создания отзыва."""
    product = await get_object_or_404(
        select(Product).
        options(joinedload(Product.user).load_only(User.username)).
        where(Product.slug == product_slug),
        session,
        get_scalar=True
    )
    validate_owner_cant_rate_own_product(product, user)
    review_fields = rating_schema.model_dump()
    review_fields.update({'user_id': user.get('id'),
                          'product_id': product.id})
    review = await session.execute(
        insert(Review).
        values(**review_fields).
        returning(*review_fields)
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
    get_object_or_404(
        select(Product).
        where(Product.slug == product_slug),
        session,
        get_scalar=True
    )
    review = await get_object_or_404(
        select(Review).
        options(joinedload(Review.user).load_only(User.username)).
        where(Review.id == review_id),
        session,
    )
    validate_owner(review, user)
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
    get_object_or_404(
        session,
        select(Product).
        where(Product.slug == product_slug)
    )
    review = get_object_or_404(
        session,
        select(Review).
        options(joinedload(Review.user).load_only(User.username)).
        where(Review.id == review_id)
    )
    validate_owner(review, user)
    await session.delete(review)
    await session.commit()
