from typing import Annotated

from sqlalchemy import insert, select, update, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify
from fastapi import APIRouter, Depends, Path, Body, status, HTTPException

from app.schemas import ProductSchema
from app.backend.db_depends import get_db
from app.models.products import Product
from app.models.categories import Category
from app.routers.permissions import is_supplier_or_is_admin_permission

router = APIRouter(tags=['products'])


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


@router.get('/products/')
async def get_all_products(
    session: Annotated[AsyncSession, Depends(get_db)]
):
    products = await session.scalars(select(Product))
    return products.all()


@router.get('/products/{product_slug}/')
async def get_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_slug: Annotated[str, Path()]
):
    product = await get_object_or_404(
        session, Product, Product.slug == product_slug
    )
    return product


@router.get('/categories/{category_slug}/products/')
async def get_all_products_by_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_slug: Annotated[str, Path()]
):
    category = await get_object_or_404(
        session, Category, Category.slug == category_slug
    )
    products = await session.scalars(
        select(Product).
        join(Category, Category.id == Product.category_id).
        where(or_(Product.category_id == category.id,
                  Category.parent_id == category.id)
              )
    )
    return products.all()


@router.post('/products/', status_code=status.HTTP_201_CREATED)
async def create_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_schema: Annotated[ProductSchema, Body()],
    user: Annotated[dict, Depends(is_supplier_or_is_admin_permission)]
):
    await get_object_or_404(
        session, Category, Category.id == product_schema.category_id
    )
    product = product_schema.model_dump()
    product.update({'slug': slugify(product.get('name')),
                    'owner_id': user.get('id')})
    await session.execute(
        insert(Product).
        values(**product)
    )
    await session.commit()
    return product


@router.put('/products/{product_slug}/')
async def update_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_slug: Annotated[str, Path()],
    product_schema: Annotated[ProductSchema, Path()],
    user: Annotated[dict, Depends(is_supplier_or_is_admin_permission)]
):
    await get_object_or_404(
        session, Category, Category.id == product_schema.category_id
    )
    product = await get_object_or_404(
        session, Product, Product.slug == product_slug, option=Product.user
    )
    if product.user.username != user.get('username'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нельзя изменить чужой продукт'
        )
    product = product_schema.model_dump()
    product.update({'slug': slugify(product.get('name')),
                    'owner_id': user.get('id')})
    await session.execute(
        update(Product).
        where(Product.slug == product_slug).
        values(**product)
    )
    await session.commit()
    return product


@router.delete('/products/{product_slug}/',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_slug: Annotated[str, Path()],
    user: Annotated[dict, Depends(is_supplier_or_is_admin_permission)]
):
    product = await get_object_or_404(
        session, Product, Product.slug == product_slug, option=Product.user
    )
    if product.user.username != user.get('username'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нельзя изменить чужой продукт'
        )
    await session.delete(product)
    await session.commit()
