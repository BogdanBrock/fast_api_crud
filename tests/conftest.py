"""Модуль для создания фикстур."""

from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from app.core.db import Base, db_session
from app.main import app

TEST_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={'check_same_thread': False}
)

test_async_session = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def test_init_db():
    """Фикстура для инициализации тестовой БД."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для создания тестовой сессии."""
    async with test_async_session() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def override_session(test_db_session) -> None:
    """Фикстура для переопределения сессии в приложении."""
    async def mock_get_session():
        yield test_db_session
    app.dependency_overrides = {}
    app.dependency_overrides[db_session] = mock_get_session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Фикстура для создания анонимного клиента."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as client:
        yield client


pytest_plugins = (
    'tests.fixtures.fixture_categories',
    'tests.fixtures.fixture_products',
    'tests.fixtures.fixture_reviews',
    'tests.fixtures.fixture_users'
)
