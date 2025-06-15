"""Модуль создания фикстур для продуктов."""

import pytest
import pytest_asyncio
from slugify import slugify

from app.models import Product
from ..utils import create_db_obj

LIST_URL = '/api/v1/products/'
DETAIL_URL = LIST_URL + '{slug}/'


@pytest.fixture
def product_request(category_1):
    return {
        'name': 'продукт 1',
        'description': 'описание 1',
        'image_url': 'https://image1.com/',
        'price': 1,
        'stock': 1,
        'category_slug': category_1.slug
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
async def product_1(test_db_session, product_request, supplier_1):
    product = Product(
        name=product_request['name'],
        slug=slugify(product_request['name']),
        description=product_request['description'],
        image_url=product_request['image_url'],
        price=product_request['price'],
        stock=product_request['stock'],
        category_slug=product_request['category_slug'],
        user_username=supplier_1.username
    )
    return await create_db_obj(test_db_session, product)


@pytest_asyncio.fixture
async def product_2(test_db_session, category_1, supplier_2):
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
def product_fields():
    return (
        'id', 'name', 'slug', 'description', 'image_url', 'price',
        'stock', 'category_slug', 'user_username', 'rating'
    )
