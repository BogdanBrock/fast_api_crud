"""Модуль для создания маршрутов."""

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.permissions import is_admin_permission
from app.api.validators import check_category_exists, check_object_duplicate
from app.crud.category import category_crud
from app.core.db import db_session
from app.schemas.category import CategorySchema

router = APIRouter()


@router.get('/')
async def get_categories(
    category_slug: str = None,
    session: AsyncSession = Depends(db_session)
):
    """
    Маршрут для получения всех категорий.

    А так же получение подкатегорий, фильтруя по категории.
    """
    if category_slug:
        return await category_crud.get_subcategories_by_category(
            category_slug, session
        )
    return await category_crud.get_all(session)


@router.get(
    '/{category_slug}/'
)
async def get_category(
    category_slug: str,
    session: AsyncSession = Depends(db_session)
):
    """Маршрут для получения категории."""
    category = await category_crud.get_object_by_slug(category_slug, session)
    await check_category_exists(category)
    return category


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=CategorySchema,
    dependencies=(Depends(is_admin_permission),)
)
async def create_category(
    category_schema: CategorySchema,
    session: AsyncSession = Depends(db_session)
):
    """Маршрут для создания категории."""
    category = await category_crud.get_object_by_slug(
        category_schema.slug, session
    )
    await check_object_duplicate(category)
    return await category_crud.create(category_schema, session)


@router.put(
    '/{category_slug}/',
    response_model=CategorySchema,
    dependencies=(Depends(is_admin_permission),)
)
async def update_category(
    category_slug: str,
    category_schema: CategorySchema,
    session: AsyncSession = Depends(db_session),
):
    """Маршрут для изменения категории."""
    category = await category_crud.get_object_by_slug(category_slug, session)
    await check_category_exists(category)
    return await category_crud.update(category, category_schema, session)


@router.delete(
    '/{category_slug}/',
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    dependencies=(Depends(is_admin_permission),)
)
async def delete_category(
    category_slug: str,
    session: AsyncSession = Depends(db_session)
) -> None:
    """Маршрут для удаления категории."""
    category = await category_crud.get_object_by_slug(category_slug, session)
    await check_category_exists(category_slug)
    await category_crud.delete(category, session)
