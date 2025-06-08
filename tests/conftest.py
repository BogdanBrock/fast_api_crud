"""Модуль для создания фикстур."""

from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport


import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from app.core.db import Base
from app.main import app
from app.core.db import db_session

BASE_URL = '/api/v1'
TEST_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'

test_engine = create_async_engine(TEST_DATABASE_URL, future=True)

test_async_session = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False
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
async def override_session(test_db_session):
    """Фикстура для переопределения сессии в прилоежении."""
    async def mock_get_session():
        yield test_db_session
    app.dependency_overrides = {}
    app.dependency_overrides[db_session] = mock_get_session


pytest_plugins = (
    'tests.fixtures.categories',
    'tests.fixtures.products',
    'tests.fixtures.users'
)
