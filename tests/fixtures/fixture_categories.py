"""Модуль создания фикстур для пользователей."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify

from app.models import Category
from ..utils import create_db_obj


@pytest_asyncio.fixture
async def parent_category(test_db_session: AsyncSession) -> Category:
    """Фикстура для создания родительской категории."""
    name = 'категория 2'
    category = Category(
        name=name,
        slug=slugify(name)
    )
    return await create_db_obj(test_db_session, category)


@pytest_asyncio.fixture
async def category_1(test_db_session: AsyncSession) -> Category:
    """Фикстура для создания категории 1."""
    name = 'категория 3'
    category = Category(name=name, slug=slugify(name))
    return await create_db_obj(test_db_session, category)


@pytest_asyncio.fixture
async def category_2(
    test_db_session: AsyncSession,
    parent_category: Category
) -> Category:
    """Фикстура для создания категории 2."""
    name = 'категория 4'
    category = Category(
        name=name,
        slug=slugify(name),
        parent_slug=parent_category.slug
    )
    return await create_db_obj(test_db_session, category)


@pytest_asyncio.fixture
async def category_3(
    test_db_session: AsyncSession,
    parent_category: Category
) -> Category:
    """Фикстура для создания категории 3."""
    name = 'категория 5'
    category = Category(
        name=name,
        slug=slugify(name),
        parent_slug=parent_category.slug
    )
    return await create_db_obj(test_db_session, category)


@pytest.fixture
def category_fields() -> tuple[str, ...]:
    return ('id', 'name', 'slug', 'parent_slug')
