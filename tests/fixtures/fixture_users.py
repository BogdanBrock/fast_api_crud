"""Модуль создания фикстур для пользователей."""

from typing import Final, AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient, ASGITransport

from app.core.user import bcrypt_context, get_current_user, create_access_token
from app.core.config import settings
from app.main import app
from app.models import User, RoleEnum
from ..utils import create_db_obj

TEST_PASSWORD: Final = 'password12345'


@pytest_asyncio.fixture
async def customer(test_db_session: AsyncSession) -> User:
    user = User(
        first_name='user',
        last_name='user',
        username='user',
        email='user@yandex.ru',
        password=bcrypt_context.hash(TEST_PASSWORD),
        role=RoleEnum.CUSTOMER
    )
    return await create_db_obj(test_db_session, user)


@pytest_asyncio.fixture
async def supplier_1(test_db_session: AsyncSession) -> User:
    user = User(
        first_name='supplier_1',
        last_name='supplier_1',
        username='supplier_1',
        email='supplier_1@yandex.ru',
        password=bcrypt_context.hash(TEST_PASSWORD),
        role=RoleEnum.SUPPLIER
    )
    return await create_db_obj(test_db_session, user)


@pytest_asyncio.fixture
async def supplier_2(test_db_session: AsyncSession) -> User:
    user = User(
        first_name='supplier_2',
        last_name='supplier_2',
        username='supplier_2',
        email='supplier_2@yandex.ru',
        password=bcrypt_context.hash(TEST_PASSWORD),
        role=RoleEnum.SUPPLIER
    )
    return await create_db_obj(test_db_session, user)


@pytest_asyncio.fixture
async def admin(test_db_session: AsyncSession) -> User:
    user = User(
        first_name='admin',
        last_name='admin',
        username='admin',
        email='admin@yandex.ru',
        password=bcrypt_context.hash(TEST_PASSWORD),
        role=RoleEnum.ADMIN
    )
    return await create_db_obj(test_db_session, user)


@pytest_asyncio.fixture
async def customer_client(customer: User) -> AsyncGenerator[AsyncClient, None]:
    """Фикстура создания клиента для покупателя."""
    app.dependency_overrides[get_current_user] = lambda: customer
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as client:
        yield client


@pytest_asyncio.fixture
async def supplier_1_client(
    supplier_1: User
) -> AsyncGenerator[AsyncClient, None]:
    """Фикстура создания клиента для поставщика товаров."""
    app.dependency_overrides[get_current_user] = lambda: supplier_1
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as client:
        yield client


@pytest_asyncio.fixture
async def supplier_2_client(
    supplier_2: User
) -> AsyncGenerator[AsyncClient, None]:
    """Фикстура создания клиента для другого поставщика товаров."""
    app.dependency_overrides[get_current_user] = lambda: supplier_2
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as client:
        yield client


@pytest_asyncio.fixture
async def admin_client(admin: User) -> AsyncGenerator[AsyncClient, None]:
    """Фикстура создания клиента для админа."""
    app.dependency_overrides[get_current_user] = lambda: admin
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as client:
        yield client
