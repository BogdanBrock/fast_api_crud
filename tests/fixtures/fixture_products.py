"""Модуль создания фикстур для продуктов."""

from typing import Any

import pytest
import pytest_asyncio
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category, Product, User
from ..utils import create_db_obj


@pytest.fixture
def product_request_data(category_1: Category) -> dict[str, Any]:
    """Фикстура для получения данных запроса продукта."""
    return {
        'name': 'продукт 1',
        'description': 'описание 1',
        'image_url': 'https://image1.com/',
        'price': 1,
        'stock': 1,
        'category_slug': category_1.slug
    }


@pytest.fixture
def product_response_data(
    product_request_data: dict[str, Any]
) -> dict[str, Any]:
    """Фикстура для получения ожидаемых данных продукта."""
    return {
        'id': 1,
        'name': product_request_data['name'],
        'slug': slugify(product_request_data['name']),
        'description': product_request_data['description'],
        'image_url': product_request_data['image_url'],
        'price': product_request_data['price'],
        'stock': product_request_data['stock'],
        'category_slug': product_request_data['category_slug'],
        'rating': 0
    }


@pytest_asyncio.fixture
async def product_1(
    test_db_session: AsyncSession,
    product_request_data: dict[str, Any],
    supplier_1: User
) -> Product:
    """Фикстура для создания продукта."""
    product = Product(
        name=product_request_data['name'],
        slug=slugify(product_request_data['name']),
        description=product_request_data['description'],
        image_url=product_request_data['image_url'],
        price=product_request_data['price'],
        stock=product_request_data['stock'],
        category_slug=product_request_data['category_slug'],
        user_username=supplier_1.username
    )
    return await create_db_obj(test_db_session, product)


@pytest_asyncio.fixture
async def product_2(
    test_db_session: AsyncSession,
    category_1: Category,
    supplier_2: User
) -> Product:
    """Фикстура для создания продукта."""
    name = 'продукт 3'
    product = Product(
        name=name,
        slug=slugify(name),
        description='описание 3',
        image_url='https://image3.com',
        price=3,
        stock=3,
        category_slug=category_1.slug,
        user_username=supplier_2.username
    )
    return await create_db_obj(test_db_session, product)


@pytest.fixture
def product_fields() -> tuple[str, ...]:
    """Фикстура с ожидаемыми полями продукта."""
    return (
        'id', 'name', 'slug', 'description', 'image_url', 'price',
        'stock', 'category_slug', 'user_username', 'rating'
    )
