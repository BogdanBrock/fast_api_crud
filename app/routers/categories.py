from typing import Annotated

from fastapi import APIRouter, status, Depends, Path, Body
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify

from app.core.dependencies import get_db
from app.core.exceptions import get_object_or_404
from app.core.permissions import is_admin_permission
from app.schemas import CategorySchema
from app.models.categories import Category

router = APIRouter(prefix='/categories', tags=['category'])


@router.get('/')
async def get_all_categories(
    session: Annotated[AsyncSession, Depends(get_db)]
):
    categories = await session.scalars(select(Category))
    return categories.all()


@router.get('/{category_slug}/')
async def get_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_slug: str
):
    category = await get_object_or_404(
        session,
        select(Category).
        where(Category.slug == category_slug)
    )
    return category


@router.post('/', status_code=status.HTTP_201_CREATED,
             dependencies=(is_admin_permission,))
async def create_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_schema: Annotated[CategorySchema, Body()]
):
    category = category_schema.model_dump()
    category['slug'] = slugify(category.get('name'))
    await session.execute(
        insert(Category).
        values(**category)
    )
    await session.commit()
    return category


@router.put('/{category_slug}/',
            dependencies=(is_admin_permission,))
async def update_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_schema: Annotated[CategorySchema, Body()],
    category_slug: Annotated[str, Path()]
):
    category = await get_object_or_404(
        session,
        select(Category).
        where(Category.slug == category_slug)
    )
    category = category_schema.model_dump()
    category['slug'] = slugify(category.get('name'))
    session.execute(
        update(Category).
        where(Category.slug == category_slug).
        values(**category)
    )
    await session.commit()
    return category


@router.delete('/{category_slug}/',
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=(is_admin_permission,))
async def delete_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_slug: Annotated[str, Path()]
):
    category = await get_object_or_404(
        session,
        select(Category).
        where(Category.slug == category_slug)
    )
    await session.delete(category)
    await session.commit()
