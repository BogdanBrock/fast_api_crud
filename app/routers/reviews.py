from typing import Annotated

from fastapi import APIRouter, Depends, Path, Body, status
from sqlalchemy import select, insert, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import ReviewSchema
from app.core.dependencies import get_db
from app.core.exceptions import get_object_or_404
from app.core.validators import (validate_owner,
                                 validate_owner_cant_rate_own_product)
from app.models.reviews import Review
from app.models.products import Product
from app.routers.auth import get_current_user

router = APIRouter(tags=['reviews'])


@router.get('/reviews/')
async def get_all_reviews(
    session: Annotated[AsyncSession, Depends(get_db)]
):
    reviews = await session.scalars(select(Review))
    return reviews.all()


@router.get('/reviews/{review_id}/')
async def get_review(
    session: Annotated[AsyncSession, Depends(get_db)],
    review_id: Annotated[int, Path()]
):
    review = await get_object_or_404(
        session, Review, Review.id == review_id
    )
    return review


@router.get('/products/{product_slug}/reviews/')
async def get_all_reviews_for_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_slug: Annotated[str, Path()]
):
    product = await get_object_or_404(
        session,
        select(Product).
        where(Product.slug == product_slug)
    )
    return product.reviews


@router.post('/products/{product_slug}/reviews/',
             status_code=status.HTTP_201_CREATED)
async def create_review(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    rating_schema: Annotated[ReviewSchema, Body()],
    product_slug: Annotated[str, Path()]
):
    product = await get_object_or_404(
        session,
        select(Product).
        options(joinedload(Product.user)).
        where(Product.slug == product_slug)
    )
    validate_owner_cant_rate_own_product(product, user)
    review = rating_schema.model_dump()
    review.update({'user_id': user.get('id'),
                   'product_id': product.id})
    session.execute(
        insert(Review).
        values(**review)
    )
    return review


@router.put('/products/{product_slug}/reviews/{review_id}/')
async def update_review(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    review_schema: Annotated[ReviewSchema, Body()],
    product_slug: Annotated[str, Path()],
    review_id: Annotated[int, Path()]
):
    get_object_or_404(
        session,
        select(Product).
        where(Product.slug == product_slug)
    )
    review = await get_object_or_404(
        session, Review, Review.id == review_id, option=Review.user
    )
    validate_owner(review, user)
    review = review_schema.model_dump()
    await session.execute(
        update(Review).
        where(Review.id == review_id).
        values(**review)
    )
    await session.commit()
    return review


@router.delete('/products/{product_slug}/reviews/{review_id}/',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    product_slug: Annotated[str, Path()],
    review_id: Annotated[int, Path()]
):
    get_object_or_404(
        session,
        select(Product).
        where(Product.slug == product_slug)
    )
    review = get_object_or_404(
        session,
        select(Review).
        options(joinedload(Review.user)).
        where(Review.id == review_id)
    )
    validate_owner(review, user)
    await session.delete(review)
    await session.commit()
