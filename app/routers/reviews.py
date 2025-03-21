from typing import Annotated

from fastapi import APIRouter, Depends, Path, Body, HTTPException, status
from sqlalchemy import select, insert, update, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import ReviewSchema
from app.models.reviews import Review
from app.models.products import Product
from app.backend.db_depends import get_db
from app.routers.auth import get_current_user

router = APIRouter(tags=['reviews'])


async def get_object_or_404(session, model, *filters, option=None):
    query = select(model).where(*filters)
    if option:
        query = query.options(joinedload(option))
    obj = await session.scalar(query)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{model.__name__} не найден.'
        )
    return obj


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
        session, Product, Product.slug == product_slug, option=Product.reviews
    )
    return product.reviews


@router.post('/products/{product_slug}/reviews/',
             status_code=status.HTTP_201_CREATED)
async def create_review(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_slug: Annotated[str, Path()],
    rating_schema: Annotated[ReviewSchema, Body()],
    user: Annotated[dict, Depends(get_current_user)]
):
    product = await get_object_or_404(
        session, Product, Product.slug == product_slug, option=Product.user
    )
    if product.user.username == user.get('username'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нельзя оставить отзыв на свой товар'
        )
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
    product_slug: Annotated[str, Path()],
    review_id: Annotated[int, Path()],
    review_schema: Annotated[ReviewSchema, Body()],
    user: Annotated[dict, Depends(get_current_user)]
):
    get_object_or_404(
        session, Product, Product.slug == product_slug
    )
    review = await session.scalar(
        select(Review).
        options(joinedload(Review.user)).
        where(Review.id == review_id)
    )
    review = await get_object_or_404(
        session, Review, Review.id == review_id, option=Review.user
    )
    if review.user.username != user.get('username'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нельзя изменить чужой отзыв'
        )
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
    product_slug: Annotated[str, Path()],
    review_id: Annotated[int, Path()],
    user: Annotated[dict, Depends(get_current_user)]
):
    await get_object_or_404(
        session, Product, Product.slug == product_slug
    )
    review = await get_object_or_404(
        session, Review, Review.id == review_id, option=Review.user
    )
    if review.user.username != user.get('username'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нельзя удалить чужой отзыв'
        )
    await session.delete(review)
    await session.commit()
