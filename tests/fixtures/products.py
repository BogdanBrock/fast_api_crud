"""Модуль создания фикстур для продуктов."""

import pytest
import pytest_asyncio
from slugify import slugify

from app.models import Product
from ..utils import create_db_obj
from ..conftest import BASE_URL

LIST_URL = f'{BASE_URL}/products/'
DETAIL_URL = LIST_URL + '{slug}/'


@pytest.fixture
def product_request(category):
    return {
        'name': 'продукт 1',
        'description': 'описание 1',
        'image_url': 'https://image1.com/',
        'price': 1,
        'stock': 1,
        'category_slug': category.slug
    }


@pytest.fixture
def product_response(product_request):
    return {
        'id': 1,
        'name': product_request['name'],
        'slug': slugify(product_request['name']),
        'description': product_request['description'],
        'image_url': product_request['image_url'],
        'price': product_request['price'],
        'stock': product_request['stock'],
        'category_slug': product_request['category_slug'],
        'rating': 0
    }


@pytest_asyncio.fixture
async def product(test_db_session, category, supplier):
    name = 'продукт 2'
    product = Product(
        name=name,
        slug=slugify(name),
        description='описание 2',
        image_url='https://image2.com',
        price=2,
        stock=2,
        category_slug=await category.awaitable_attrs.slug,
        user_username=await supplier.awaitable_attrs.username
    )
    return await create_db_obj(test_db_session, product)


@pytest.fixture
def product_fields():
    return (
        'id', 'name', 'slug', 'description', 'image_url', 'price',
        'stock', 'category_slug', 'user_username', 'rating'
    )
