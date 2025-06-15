"""Модуль создания фикстур для пользователей."""

import pytest
import pytest_asyncio
from slugify import slugify

from app.models import Category
from ..utils import create_db_obj

LIST_URL = '/api/v1/categories/'
DETAIL_URL = LIST_URL + '{slug}/'


@pytest.fixture
def category_request():
    """Фикстура для запроса категории."""
    return {'name': 'категория 1'}


@pytest.fixture
def category_response(category_request):
    """Фикстура для ответных данных категории."""
    return {
        'id': 1,
        'name': category_request['name'],
        'slug': slugify(category_request['name']),
        'parent_slug': None
    }


@pytest_asyncio.fixture
async def parent_category(test_db_session, category_request):
    """Фикстура для создания родительской категории."""
    category = Category(
        name=category_request['name'],
        slug=slugify(category_request['name'])
    )
    return await create_db_obj(test_db_session, category)


@pytest_asyncio.fixture
async def category_1(test_db_session, parent_category):
    """Фикстура для создания категории 1."""
    name = 'категория 2'
    category = Category(
        name=name,
        slug=slugify(name),
        parent_slug=parent_category.slug
    )
    return await create_db_obj(test_db_session, category)


@pytest_asyncio.fixture
async def category_2(test_db_session, parent_category):
    """Фикстура для создания категории 2."""
    name = 'категория 3'
    category = Category(
        name=name,
        slug=slugify(name),
        parent_slug=parent_category.slug
    )
    return await create_db_obj(test_db_session, category)


@pytest.fixture
def category_fields():
    return ('id', 'name', 'slug', 'parent_slug')
