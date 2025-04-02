"""Модуль для создания маршрутов."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.permissions import (RequestContext,
                                 is_owner_or_admin_permission)
from app.api.validators import (check_cant_review_own_product,
                                check_review_already_exists,
                                get_product_or_not_found,
                                get_review_or_not_found)
from app.core.db import db_session
from app.core.user import get_current_user
from app.crud import review_crud
from app.models import User
from app.schemas.review import (ReviewCreateSchema,
                                ReviewReadSchema,
                                ReviewUpdateSchema)

router = APIRouter()


@router.get(
    '/reviews/',
    response_model=list[ReviewReadSchema]
)
async def get_reviews(
    product_slug: str = None,
    session: AsyncSession = Depends(db_session),
):
    """Маршрут для получения всех отзывов или по фильтру продукта."""
    return await review_crud.get_reviews_by_product_or_all(
        product_slug,
        session
    )


@router.get(
    '/products/{product_slug}/reviews/{review_id}/',
    response_model=ReviewReadSchema
)
async def get_review(
    product_slug: str,
    review_id: int,
    session: AsyncSession = Depends(db_session),
):
    """Маршрут для получения отзыва."""
    await get_product_or_not_found(product_slug, session)
    return await get_review_or_not_found(review_id, session)


@router.post(
    '/products/{product_slug}/reviews/',
    status_code=status.HTTP_201_CREATED,
    response_model=ReviewReadSchema
)
async def create_review(
    product_slug: str,
    review_schema: ReviewCreateSchema,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_session),
):
    """Маршрут для создания отзыва."""
    product = await get_product_or_not_found(product_slug, session)
    await check_cant_review_own_product(user.username, product.user_username)
    await check_review_already_exists(product.slug, user.username, session)
    return await review_crud.create(review_schema, session, user, product_slug)


@router.patch(
    '/products/{product_slug}/reviews/{review_id}/',
    response_model=ReviewReadSchema
)
async def update_review(
    schema: ReviewUpdateSchema,
    cxt: RequestContext = Depends(is_owner_or_admin_permission),
):
    """Маршрут для изменения отзыва."""
    return await review_crud.update(cxt['model_obj'], schema, cxt['session'])


@router.delete(
    '/products/{product_slug}/reviews/{review_id}/',
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None
)
async def delete_review(
    cxt: RequestContext = Depends(is_owner_or_admin_permission),
):
    """Маршрут для удаления отзыва."""
    await review_crud.delete(cxt['model_obj'], cxt['session'])
