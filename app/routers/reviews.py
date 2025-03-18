from typing import Annotated

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy import select, insert
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import Review
from app.models.products import Product
from app.backend.db_depends import get_db
from app.routers.permissions import is_supplier_or_is_admin_permission
from app.schemas import ReviewSchema
from app.routers.auth import get_current_user

router = APIRouter(tags=['reviews'])


@router.get('/reviews')
async def all_reviews(
    session: Annotated[AsyncSession, Depends(get_db)]
):
    reviews = await session.scalars(select(Review))
    reviews = reviews.all()
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет каких-либо оценок'
        )
    return reviews


@router.get('/products/{product_slug}/reviews')
async def all_reviews_for_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_slug: Annotated[str, Path()]
):
    product = await session.scalar(
        select(Product).
        options(joinedload(Product.reviews)).
        where(Product.slug == product_slug)
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет такого продукта'
        )
    reviews = product.reviews
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет каких-либо оценок'
        )
    return reviews


@router.post('/products/{product_slug}/reviews',
             status_code=status.HTTP_201_CREATED)
async def create_review(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_slug: Annotated[str, Path()],
    rating_schema: ReviewSchema,
    user: Annotated[dict, Depends(get_current_user)]
):
    product = await session.scalar(
        select(Product).
        options(joinedload(Product.user)).
        where(Product.slug == product_slug)
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет такого продукта'
        )
    if product.user.username == user.get('username'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нельзя оставить отзыв на свой товар'
        )
    await session.execute(
        insert(Review).
        values(**rating_schema.model_dump(),
               user_id=user.get('id'),
               product_id=product.id)
    )
    await session.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Succesful'
    }


@router.put('/products/{product_slug}/reviews/{review_id}')
async def update_review(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_slug: str,
    review_id: int,
    review_schema: ReviewSchema,
    user: Annotated[dict, Depends(get_current_user)]
):
    product = await session.scalar(
        select(Product).
        where(Product.slug == product_slug)
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет такого продукта'
        )
    review = await session.scalar(
        select(Review).
        options(joinedload(Review.user)).
        where(Review.id == review_id)
    )
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет такого отзыва'
        )
    if review.user.username != user.get('username'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нельзя изменить чужой отзыв'
        )
    review.text = review_schema.text
    review.grade = review_schema.grade
    await session.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product update is successful'
    }


@router.delete('/products/{product_slug}/reviews/{review_id}',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_slug: str,
    review_id: int,
    user: Annotated[dict, Depends(get_current_user)]
):
    product = await session.scalar(
        select(Product).
        where(Product.slug == product_slug)
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет такого продукта'
        )
    review = await session.scalar(
        select(Review).
        options(joinedload(Review.user)).
        where(Review.id == review_id)
    )
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет такого отзыва'
        )
    if review.user.username != user.get('username'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нельзя удалить чужой отзыв'
        )
    await session.delete(review)
    await session.commit()
