"""Модуль для создания маршрутов."""

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.permissions import RequestContext, is_admin_permission
from app.api.validators import (get_category_or_not_found,
                                check_category_already_exists)
from app.crud.category import category_crud
from app.core.db import db_session
from app.schemas.category import (CategoryCreateSchema,
                                  CategoryUpdateSchema,
                                  CategoryReadSchema)

router = APIRouter()


@router.get(
    '/',
    response_model=list[CategoryReadSchema]
)
async def get_categories(
    parent_slug: str = None,
    session: AsyncSession = Depends(db_session)
):
    """Маршрут для получения всех категорий. """

    """Так же подкатегорий по фильтру категорий."""
    return await category_crud.get_subcategories_by_category_or_all(
        parent_slug,
        session
    )


@router.get(
    '/{category_slug}/',
    response_model=CategoryReadSchema
)
async def get_category(
    category_slug: str,
    session: AsyncSession = Depends(db_session)
):
    """Маршрут для получения категории."""
    return await get_category_or_not_found(category_slug, session)


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=CategoryReadSchema
)
async def create_category(
    schema: CategoryCreateSchema,
    cxt: RequestContext = Depends(is_admin_permission)
):
    """Маршрут для создания категории."""
    if schema.parent_slug:
        await get_category_or_not_found(schema.parent_slug, cxt['session'])
    await check_category_already_exists(schema.slug, cxt['session'])
    return await category_crud.create(schema, cxt['session'])


@router.patch(
    '/{category_slug}/',
    response_model=CategoryReadSchema
)
async def update_category(
    schema: CategoryUpdateSchema,
    cxt: RequestContext = Depends(is_admin_permission)
):
    """Маршрут для изменения категории."""
    return await category_crud.update(cxt['model_obj'], schema, cxt['session'])


@router.delete(
    '/{category_slug}/',
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None
)
async def delete_category(
    cxt: RequestContext = Depends(is_admin_permission)
):
    """Маршрут для удаления категории."""
    await category_crud.delete(cxt['model_obj'], cxt['session'])
