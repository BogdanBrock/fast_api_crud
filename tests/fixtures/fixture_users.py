"""Модуль создания фикстур для пользователей."""

from typing import Any, AsyncGenerator, Final

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import bcrypt_context, get_current_user
from app.main import app
from app.models import RoleEnum, User
from ..utils import create_db_obj

TEST_PASSWORD: Final = 'password12345'


@pytest.fixture
def user_request_data() -> dict[str, str]:
    """Фикстура для получения данных запроса пользователя."""
    return {
            'first_name': 'test_user',
            'last_name': 'test_user',
            'username': 'test_user',
            'email': 'test_user@example.com',
            'password': 'test_password12345'
        }


@pytest.fixture
def user_response_data(user_request_data: dict[str, str]) -> dict[str, Any]:
    """Фикстура для получения ожидаемых данных пользователя."""
    return {
        'id': 1,
        'first_name': user_request_data['first_name'],
        'last_name': user_request_data['last_name'],
        'username': user_request_data['username'],
        'email': user_request_data['email'],
    }


@pytest_asyncio.fixture
async def customer(test_db_session: AsyncSession) -> User:
    """Фикстура для создания покупателя."""
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
    """Фикстура для создания поставщика."""
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
    """Фикстура для создания поставщика."""
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
    """Фикстура для создания администратора."""
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
    """Фикстура создания клиента для поставщика товаров."""
    app.dependency_overrides[get_current_user] = lambda: supplier_2
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as client:
        yield client


@pytest_asyncio.fixture
async def admin_client(admin: User) -> AsyncGenerator[AsyncClient, None]:
    """Фикстура создания клиента для администратора."""
    app.dependency_overrides[get_current_user] = lambda: admin
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as client:
        yield client
