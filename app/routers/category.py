from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify

from app.backend.db_depends import get_db
from app.schemas import CategorySchema
from app.models.categories import Category
from app.routers.permissions import (is_admin_permission)

router = APIRouter(prefix='/categories', tags=['category'])


@router.get('/')
async def get_all_categories(
    session: Annotated[AsyncSession, Depends(get_db)]
):
    query = select(Category).where(Category.is_active)
    categories = await session.scalars(query)
    return categories.all()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_schema: CategorySchema,
    user: None | HTTPException = Depends(
        is_admin_permission
    )
):
    slug = slugify(category_schema.name)
    query = insert(Category).values(
        name=category_schema.name,
        parent_id=category_schema.parent_id,
        slug=slug
    )
    await session.execute(query)
    await session.commit()
    return {
        'name': category_schema.name,
        'parent_id': category_schema.parent_id,
        'slug': slug
    }


@router.put('/{category_slug}')
async def update_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_slug: str,
    category_schema: CategorySchema,
    user: None | HTTPException = Depends(
        is_admin_permission
    )
):
    query = select(Category).where(Category.slug == category_slug)
    category = await session.scalar(query)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Отсутствует такая категория'
        )
    slug = slugify(category_schema.name)
    category.name = category_schema.name
    category.parent_id = category_schema.parent_id
    category.slug = slug
    await session.commit()
    return {
        'name': category_schema.name,
        'parent_id': category_schema.parent_id,
        'slug': slug
    }


@router.delete('/{category_slug}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_slug: str,
    user: None | HTTPException = Depends(
        is_admin_permission
    )
):
    query = select(Category).where(Category.slug == category_slug)
    category = await session.scalar(query)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Отсутствует такая категория'
        )
    await session.delete(category)
    await session.commit()
