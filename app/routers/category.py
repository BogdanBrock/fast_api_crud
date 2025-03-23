from typing import Annotated

from fastapi import APIRouter, status, Depends, Path, Body
from sqlalchemy import select, insert, update
from sqlalchemy.orm import load_only
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.exceptions import get_object_or_404
from app.core.permissions import is_admin_permission
from app.core.constants import CATEGORY_DATA
from app.schemas.category import CategorySchema
from app.models.category import Category

router = APIRouter(prefix='/categories', tags=['Category'])


@router.get('/')
async def get_categories(
    session: Annotated[AsyncSession, Depends(get_db)]
):
    categories = await session.execute(select(*CATEGORY_DATA))
    return categories.mappings().all()


@router.get('/{category_slug}/')
async def get_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_slug: str
):
    category = await get_object_or_404(
        select(Category).
        options(load_only(*CATEGORY_DATA)).
        where(Category.slug == category_slug),
        session,
        get_scalar=True
    )
    return category


@router.post('/', status_code=status.HTTP_201_CREATED,
             dependencies=(is_admin_permission,))
async def create_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_schema: Annotated[CategorySchema, Body()]
):
    if category_id := category_schema.parent_id:
        get_object_or_404(
            select(Category).
            where(Category.id == category_id),
            session,
            get_scalar=True
        )
    category = await session.execute(
        insert(Category).
        values(**category_schema.model_dump()).
        returning(*CATEGORY_DATA)
    )
    await session.commit()
    return category.mappings().first()


@router.put('/{category_slug}/',
            dependencies=(is_admin_permission,))
async def update_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_schema: Annotated[CategorySchema, Body()],
    category_slug: Annotated[str, Path()]
):
    get_object_or_404(
        select(Category).
        where(Category.slug == category_slug),
        session,
        get_scalar=True
    )
    category_updated = await session.execute(
        update(Category).
        where(Category.slug == category_slug).
        values(**category_schema.model_dump()).
        returning(*CATEGORY_DATA)
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
    category = await get_object_or_404(
        select(Category).
        where(Category.slug == category_slug),
        session,
        get_scalar=True
    )
    await session.delete(category)
    await session.commit()
