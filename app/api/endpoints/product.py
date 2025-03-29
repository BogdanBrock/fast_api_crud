"""Модуль для создания маршрутов."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_category_exists,
                                check_product_exists,
                                check_object_duplicate)
from app.api.permissions import (is_admin_or_supplier_permission,
                                 check_permission_for_user)
from app.core.db import db_session
from app.schemas.product import ProductSchema
from app.crud import category_crud, product_crud
from app.models import User

router = APIRouter()


@router.get('/')
async def get_products(
    category_slug: str = None,
    session: AsyncSession = Depends(db_session)
):
    """Маршрут для получения всех продуктов или продуктов по категории."""
    if category_slug:
        return await product_crud.get_products_by_category(
            category_slug, session
        )
    return await product_crud.get_all(session)


@router.get('/{product_slug}/')
async def get_product(
    product_slug: str,
    session: AsyncSession = Depends(db_session)
):
    """Маршрут для получения продукта."""
    product = await product_crud.get_object_by_slug(product_slug, session)
    await check_product_exists(product)
    return product


@router.post('/', status_code=status.HTTP_201_CREATED,)
async def create_product(
    product_schema: ProductSchema,
    user: User = Depends(is_admin_or_supplier_permission),
    session: AsyncSession = Depends(db_session)
):
    """Маршрут для создания продукта."""
    category = await category_crud.get(product_schema.category_id, session)
    await check_category_exists(category)
    product = await product_crud.get_object_by_slug(
        product_schema.slug, session
    )
    await check_object_duplicate(product)
    return await product_crud.create(product_schema, session, user)


@router.put('/{product_slug}/')
async def update_product(
    product_slug: str,
    product_schema: ProductSchema,
    user: User = Depends(is_admin_or_supplier_permission),
    session: AsyncSession = Depends(db_session)
):
    """Маршрут для изменения продукта."""
    category = await category_crud.get(product_schema.category_id, session)
    await check_category_exists(category)
    product = await product_crud.get_product_by_slug_with_user(
        product_slug, session
    )
    await check_product_exists(product)
    await check_permission_for_user(user, product.user)
    return await product_crud.update(product, product_schema, session)


@router.delete(
    '/{product_slug}/',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_product(
    product_slug: str,
    user: User = Depends(is_admin_or_supplier_permission),
    session: AsyncSession = Depends(db_session),
) -> None:
    """Маршрут для удаления продукта."""
    product = await product_crud.get_object_by_slug(product_slug, session)
    await check_product_exists(product)
    await check_permission_for_user(user, product.user)
    await product_crud.delete(product, session)
