"""Модуль для создания маршрутов."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Body, Query, status
from sqlalchemy import select, update, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import const
from app.core.db import get_db
from app.core.exceptions import NotFound
from app.core.permissions import (is_admin_or_supplier_permission,
                                  has_object_permission)
from app.schemas.product import ProductSchema
from app.models import Category, Product, User

router = APIRouter(prefix='/products', tags=['Products'])


@router.get('/')
async def get_products(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_slug: Annotated[str, Query()] = None
):
    """Маршрут для получения всех продуктов или продуктов по категории."""
    query = select(*const.PRODUCT_FIELDS)
    if category_slug:
        category_id = await session.scalar(
            select(Category.id).
            where(Category.slug == category_slug)
        )
        query = (
            query.join(Category, Category.id == Product.category_id).
            where(category_id and or_(Product.category_id == category_id,
                                      Category.parent_id == category_id))
        )
    products = await session.execute(query)
    return products.mappings().all()


@router.get('/{product_slug}/')
async def get_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_slug: Annotated[str, Path()]
):
    """Маршрут для получения продукта."""
    product = await session.execute(
        select(*const.PRODUCT_FIELDS).
        where(Product.slug == product_slug)
    )
    if product := product.mappings().first():
        return product
    raise NotFound('Такого продукта не существует.')


@router.post('/', status_code=status.HTTP_201_CREATED,)
async def create_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, is_admin_or_supplier_permission],
    product_schema: Annotated[ProductSchema, Body()]
):
    """Маршрут для создания продукта."""
    category = await session.scalar(
        select(Category).
        where(Category.id == product_schema.category_id)
    )
    if not category:
        raise NotFound('Такой категории не существует.')
    product = Product(**product_schema.model_dump(),
                      user_id=user.id)
    session.add(product)
    await session.commit()
    product_created = await session.execute(
        select(*const.PRODUCT_FIELDS).
        where(Product.id == product.id)
    )
    return product_created.mappings().first()


@router.put('/{product_slug}/')
async def update_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, is_admin_or_supplier_permission],
    product_schema: Annotated[ProductSchema, Body()],
    product_slug: Annotated[str, Path()]
):
    """Маршрут для изменения продукта."""
    category = await session.scalar(
        select(Category).
        where(Category.id == product_schema.category_id)
    )
    if not category:
        raise NotFound('Такой категории не существует.')
    product = await session.scalar(
        select(Product).
        options(joinedload(Product.user)).
        where(Product.slug == product_slug)
    )
    if not product:
        raise NotFound('Такого продукта не существует.')
    has_object_permission(user, product)
    product_updated = await session.execute(
        update(Product).
        where(Product.slug == product_slug).
        values(**product_schema.model_dump()).
        returning(*const.PRODUCT_FIELDS)
    )
    await session.commit()
    return product_updated.mappings().first()


@router.delete('/{product_slug}/',
               status_code=status.HTTP_204_NO_CONTENT,)
async def delete_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, is_admin_or_supplier_permission],
    product_slug: Annotated[str, Path()]
):
    """Маршрут для удаления продукта."""
    product = await session.scalar(
        select(Product).
        options(joinedload(Product.user)).
        where(Product.slug == product_slug)
    )
    if not product:
        raise NotFound('Такого продукта не существует.')
    has_object_permission(user, product)
    await session.delete(product)
    await session.commit()
