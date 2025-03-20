from typing import Annotated

from fastapi import APIRouter, status, Depends, Path, Body, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify

from app.backend.db_depends import get_db
from app.schemas import CategorySchema
from app.models.categories import Category
from app.routers.permissions import is_admin_permission

router = APIRouter(prefix='/categories', tags=['category'])


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
        session, Category, Category.slug == category_slug
    )
    return category


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_schema: Annotated[CategorySchema, Body()],
    user: Annotated[None, Depends(is_admin_permission)]
):
    category = category_schema.model_dump()
    category['slug'] = slugify(category.get('name'))
    await session.execute(
        insert(Category).
        values(**category)
    )
    await session.commit()
    return category


@router.put('/{category_slug}/')
async def update_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_slug: Annotated[str, Path()],
    category_schema: Annotated[CategorySchema, Path()],
    user: Annotated[None, Depends(is_admin_permission)]
):
    category = await get_object_or_404(
        session, Category, Category.slug == category_slug
    )
    category = category_schema.model_dump()
    category['slug'] = slugify(category.get('name'))
    session.execute(
        update(Category).
        where(Category.id == category.get('id')).
        values(**category)
    )
    await session.commit()
    return category


@router.delete('/{category_slug}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_slug: Annotated[str, Path()],
    user: Annotated[None, Depends(is_admin_permission)]
):
    category = await get_object_or_404(
        session, Category, Category.slug == category_slug
    )
    await session.delete(category)
    await session.commit()
