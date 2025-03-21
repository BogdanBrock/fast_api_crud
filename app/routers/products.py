from typing import Annotated

from sqlalchemy import insert, select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify
from fastapi import APIRouter, Depends, Path, Body, status

from app.core.dependencies import get_db
from app.core.exceptions import get_object_or_404
from app.core.validators import validate_owner
from app.core.permissions import is_admin_or_is_supplier_permission
from app.schemas import ProductSchema
from app.models.products import Product
from app.models.categories import Category
from app.routers.auth import get_current_user

router = APIRouter(tags=['products'])


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


@router.post('/products/', status_code=status.HTTP_201_CREATED,
             dependencies=(is_admin_or_is_supplier_permission,))
async def create_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    product_schema: Annotated[ProductSchema, Body()]
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


@router.put('/products/{product_slug}/',
            dependencies=(is_admin_or_is_supplier_permission,))
async def update_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    product_schema: Annotated[ProductSchema, Body()],
    product_slug: Annotated[str, Path()]
):
    await get_object_or_404(
        session, Category, Category.id == product_schema.category_id
    )
    product = await get_object_or_404(
        session, Product, Product.slug == product_slug, option=Product.user
    )
    validate_owner(product, user)
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
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=(is_admin_or_is_supplier_permission,))
async def delete_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    product_slug: Annotated[str, Path()]
):
    product = await get_object_or_404(
        session, Product, Product.slug == product_slug, option=Product.user
    )
    validate_owner(product, user)
    await session.delete(product)
    await session.commit()
