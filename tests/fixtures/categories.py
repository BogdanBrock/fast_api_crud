"""Модуль создания фикстур для пользователей."""

import pytest
import pytest_asyncio
from slugify import slugify

from app.models import Category
from ..utils import create_db_obj
from ..conftest import BASE_URL

LIST_URL = f'{BASE_URL}/categories/'
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
async def category(test_db_session):
    """Фикстура для создания категории."""
    name = 'категория 2'
    category = Category(name=name, slug=slugify(name))
    return await create_db_obj(test_db_session, category)


@pytest.fixture
def category_fields():
    return ('id', 'name', 'slug', 'parent_slug')
