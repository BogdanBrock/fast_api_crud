"""Модуль для создания маршрутов."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.permissions import (RequestContext,
                                 is_supplier_or_admin_permission,
                                 is_supplier_owner_or_admin_permission)
from app.api.validators import (check_product_already_exists,
                                get_category_or_not_found,
                                get_product_or_not_found)
from app.core.db import db_session
from app.crud import product_crud
from app.schemas.product import (ProductCreateSchema,
                                 ProductReadSchema,
                                 ProductUpdateSchema)

router = APIRouter()


@router.get(
    '/',
    response_model=list[ProductReadSchema]
)
async def get_products(
    category_slug: str = None,
    is_active: bool = False,
    session: AsyncSession = Depends(db_session)
):
    """
    Маршрут для получения всех продуктов по фильтру категории и наличии товара.

    Если у категории есть подкатегории, продукты из них тоже будут включены.
    """
    return await product_crud.get_products_by_category_or_is_active_or_all(
        category_slug,
        is_active,
        session
    )


@router.get(
    '/{product_slug}/',
    response_model=ProductReadSchema
)
async def get_product(
    product_slug: str,
    session: AsyncSession = Depends(db_session)
):
    """Маршрут для получения продукта."""
    return await get_product_or_not_found(product_slug, session)


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=ProductReadSchema
)
async def create_product(
    schema: ProductCreateSchema,
    cxt: RequestContext = Depends(is_supplier_or_admin_permission),
):
    """Маршрут для создания продукта."""
    await get_category_or_not_found(schema.category_slug, cxt['session'])
    await check_product_already_exists(schema.slug, cxt['session'])
    return await product_crud.create(schema, cxt['session'], cxt['user'])


@router.patch(
    '/{product_slug}/',
    response_model=ProductReadSchema
)
async def update_product(
    product_slug: str,
    schema: ProductUpdateSchema,
    cxt: RequestContext = Depends(is_supplier_owner_or_admin_permission),
):
    """Маршрут для изменения продукта."""
    return await product_crud.update(cxt['model_obj'], schema, cxt['session'])


@router.delete(
    '/{product_slug}/',
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None
)
async def delete_product(
    product_slug: str,
    cxt: RequestContext = Depends(is_supplier_owner_or_admin_permission),
):
    """Маршрут для удаления продукта."""
    await product_crud.delete(cxt['model_obj'], cxt['session'])
