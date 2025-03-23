from typing import Annotated

from sqlalchemy import select, update, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Path, Body, Query, status

from app.core.dependencies import get_db
from app.core.exceptions import get_object_or_404
from app.core.validators import validate_owner
from app.core.permissions import is_admin_or_is_supplier_permission
from app.core.constants import PRODUCT_DATA
from app.schemas.product import ProductSchema
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix='/products', tags=['Products'])


@router.get('/')
async def get_products(
    session: Annotated[AsyncSession, Depends(get_db)],
    category_slug: Annotated[str, Query()] = None
):
    query = select(*PRODUCT_DATA)
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
    product = await get_object_or_404(
        select(*PRODUCT_DATA).
        where(Product.slug == product_slug),
        session,
        get_mapping=True
    )
    return product


@router.post('/', status_code=status.HTTP_201_CREATED,
             dependencies=(is_admin_or_is_supplier_permission,))
async def create_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    product_schema: Annotated[ProductSchema, Body()]
):
    get_object_or_404(
        select(Category).
        where(Category.id == product_schema.category_id),
        session,
        get_scalar=True
    )
    product = Product(**product_schema.model_dump(),
                      user_id=user.get('id'))
    session.add(product)
    await session.commit()
    product_created = await session.execute(
        select(*PRODUCT_DATA).
        where(Product.id == product.id)
    )
    return product_created.mappings().first()


@router.put('/{product_slug}/',
            dependencies=(is_admin_or_is_supplier_permission,))
async def update_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    product_schema: Annotated[ProductSchema, Body()],
    product_slug: Annotated[str, Path()]
):
    get_object_or_404(
        select(Category).
        where(Category.id == product_schema.category_id),
        session,
        get_scalar=True
    )
    product = await get_object_or_404(
        select(Product).
        options(joinedload(Product.user).load_only(User.username)).
        where(Product.slug == product_slug),
        session,
        get_scalar=True
    )
    validate_owner(product, user)
    product_updated = await session.execute(
        update(Product).
        where(Product.slug == product_slug).
        values(**product_schema.model_dump()).
        returning(*PRODUCT_DATA)
    )
    await session.commit()
    return product_updated.mappings().first()


@router.delete('/{product_slug}/',
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=(is_admin_or_is_supplier_permission,))
async def delete_product(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
    product_slug: Annotated[str, Path()]
):
    product = await get_object_or_404(
        select(Product).
        options(joinedload(Product.user).load_only(User.username)).
        where(Product.slug == product_slug),
        session,
        get_scalar=True
    )
    validate_owner(product, user)
    await session.delete(product)
    await session.commit()
