from typing import Annotated

from sqlalchemy import insert, select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify
from fastapi import APIRouter, Depends, status, HTTPException

from app.schemas import ProductSchema
from app.backend.db_depends import get_db
from app.models.products import Product
from app.models.categories import Category
from app.models.users import User
from app.routers.permissions import (is_supplier_or_is_admin_permission)


router = APIRouter(prefix='/products', tags=['products'])


@router.get('/')
async def all_products(
    session: Annotated[AsyncSession, Depends(get_db)]
):
    query = select(Product).where(Product.stock > 0)
    products = await session.scalars(query)
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no products'
        )
    return products.all()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_schema: ProductSchema,
    user: dict = Depends(
        is_supplier_or_is_admin_permission
    )
):
    query_category = (
        select(Category).
        where(Category.id == product_schema.category)
    )
    category = await session.scalar(query_category)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )
    query = insert(Product).values(
        name=product_schema.name,
        slug=slugify(product_schema.name),
        description=product_schema.description,
        price=product_schema.price,
        image_url=product_schema.image_url,
        supplier_id=user.get('id'),
        stock=product_schema.stock,
        rating=0.0,
        category_id=product_schema.category
    )
    await session.execute(query)
    await session.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Succesful'
    }


@router.get('/{category_slug}')
async def product_by_category(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_slug: str
):
    query_category = select(Category).where(Category.slug == category_slug)
    category = await session.scalar(query_category)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category is not found'
        )
    query_subcategories = (
        select(Category).
        where(Category.parent_id == category.id)
    )
    subcategories = await session.scalars(query_subcategories)
    category_and_subcategories = [category.id] + [
        subcategory.id for subcategory in subcategories.all()
    ]
    query_products = (
        select(Product).
        where(
            Product.category_id.in_(category_and_subcategories),
            Product.stock > 0
        )
    )
    products = await session.scalars(query_products)
    return products.all()


@router.get('/detail/{product_slug}')
async def product_detail(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_slug: str
):
    query = select(Product).where(Product.slug == product_slug)
    product = await session.scalar(query)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    return product


@router.put('/{product_slug}')
async def update_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_slug: str,
    product_schema: ProductSchema,
    user: dict = Depends(
        is_supplier_or_is_admin_permission
    )
):
    query_get_product = (
        select(Product).
        options(joinedload(Product.user)).
        where(Product.slug == product_slug)
    )
    product = await session.scalar(query_get_product)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product is not found'
        )
    if product.user.username != user.get('username'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нельзя изменить чужой продукт'
        )
    query_category = (
        select(Category).
        where(Category.id == product_schema.category)
    )
    category = await session.scalar(query_category)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )
    query_update_product = (
        update(Product).
        where(Product.slug == product_slug).
        values(
            name=product_schema.name,
            slug=slugify(product_schema.name),
            description=product_schema.description,
            price=product_schema.price,
            image_url=product_schema.image_url,
            stock=product_schema.stock,
            rating=0.0,
            category_id=product_schema.category
        )
    )
    await session.execute(query_update_product)
    await session.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product update is successful'
    }


@router.delete('/{product_slug}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    product_slug: str,
    user: dict = Depends(
        is_supplier_or_is_admin_permission
    )
):
    query = (
        select(Product).
        options(joinedload(Product.user)).
        where(Product.slug == product_slug)
    )
    product = await session.scalar(query)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product is not found'
        )
    if product.user.username != user.get('username'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нельзя изменить чужой продукт'
        )
    await session.delete(product)
    await session.commit()
