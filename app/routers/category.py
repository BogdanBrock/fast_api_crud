"""Модуль для создания маршрутов."""

from typing import Annotated

from fastapi import APIRouter, status, Depends, Path, Body
from sqlalchemy import select, insert, update
from sqlalchemy.orm import load_only
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import const
from app.core.db import get_db
from app.core.exceptions import NotFound
from app.core.permissions import is_admin_permission
from app.schemas.category import CategorySchema
from app.models.category import Category

router = APIRouter(prefix='/categories', tags=['Category'])


@router.get('/')
async def get_categories(
    session: Annotated[AsyncSession, Depends(get_db)]
):
    """Маршрут для получения всех категорий."""
    categories = await session.execute(select(*const.CATEGORY_FIELDS))
    return categories.mappings().all()


@router.get('/{category_slug}/')
async def get_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_slug: str
):
    """Маршрут для получения категории."""
    category = await session.scalar(
        select(Category).
        options(load_only(*const.CATEGORY_FIELDS)).
        where(Category.slug == category_slug)
    )
    if not category:
        raise NotFound('Такой категории не существует.')
    return category


@router.post('/', status_code=status.HTTP_201_CREATED,
             dependencies=(is_admin_permission,))
async def create_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_schema: Annotated[CategorySchema, Body()]
):
    """Маршрут для создания категории."""
    if category_schema.parent_id:
        category_parent = await session.scalar(
            select(Category).
            where(Category.id == category_schema.parent_id)
        )
        if not category_parent:
            raise NotFound('Такой родительской категории не существует.')
    category = await session.execute(
        insert(Category).
        values(**category_schema.model_dump()).
        returning(*const.CATEGORY_FIELDS)
    )
    await session.commit()
    return category.mappings().first()


@router.put('/{category_slug}/', dependencies=(is_admin_permission,))
async def update_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_schema: Annotated[CategorySchema, Body()],
    category_slug: Annotated[str, Path()]
):
    """Маршрут для изменения категории."""
    category = await session.scalar(
        select(Category).
        where(Category.slug == category_slug)
    )
    if not category:
        raise NotFound('Такой категории не существует.')
    category_updated = await session.execute(
        update(Category).
        where(Category.slug == category_slug).
        values(**category_schema.model_dump()).
        returning(*const.CATEGORY_FIELDS)
    )
    await session.commit()
    return category_updated.mappings().first()


@router.delete('/{category_slug}/',
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=(is_admin_permission,))
async def delete_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_slug: Annotated[str, Path()]
):
    """Маршрут для удаления категории."""
    category = await session.scalar(
        select(Category).
        where(Category.slug == category_slug)
    )
    if not category:
        raise NotFound('Такой категории не существует.')
    await session.delete(category)
    await session.commit()
