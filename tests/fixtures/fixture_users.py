"""Модуль создания фикстур для пользователей."""

import pytest_asyncio

from httpx import AsyncClient, ASGITransport

from app.core.user import get_hashed_password, get_current_user
from app.main import app
from app.models import User, RoleEnum
from ..utils import create_db_obj


@pytest_asyncio.fixture
async def customer(test_db_session):
    user = User(
        first_name='user',
        last_name='user',
        username='user',
        email='user@yandex.ru',
        password=get_hashed_password('password12345'),
        role=RoleEnum.CUSTOMER
    )
    return await create_db_obj(test_db_session, user)


@pytest_asyncio.fixture
async def supplier_1(test_db_session):
    user = User(
        first_name='supplier_1',
        last_name='supplier_1',
        username='supplier_1',
        email='supplier_1@yandex.ru',
        password=get_hashed_password('password12345'),
        role=RoleEnum.SUPPLIER
    )
    return await create_db_obj(test_db_session, user)


@pytest_asyncio.fixture
async def supplier_2(test_db_session):
    user = User(
        first_name='supplier_2',
        last_name='supplier_2',
        username='supplier_2',
        email='supplier_2@yandex.ru',
        password=get_hashed_password('password12345'),
        role=RoleEnum.SUPPLIER
    )
    return await create_db_obj(test_db_session, user)


@pytest_asyncio.fixture
async def admin(test_db_session):
    user = User(
        first_name='admin',
        last_name='admin',
        username='admin',
        email='admin@yandex.ru',
        password=get_hashed_password('password12345'),
        role=RoleEnum.ADMIN
    )
    return await create_db_obj(test_db_session, user)


@pytest_asyncio.fixture
async def customer_client(customer):
    """Фикстура создания клиента для покупателя."""
    app.dependency_overrides[get_current_user] = lambda: customer
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture
async def supplier_1_client(supplier_1):
    """Фикстура создания клиента для поставщика товаров."""
    app.dependency_overrides[get_current_user] = lambda: supplier_1
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture
async def supplier_2_client(supplier_2):
    """Фикстура создания клиента для другого поставщика товаров."""
    app.dependency_overrides[get_current_user] = lambda: supplier_2
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_client(admin):
    """Фикстура создания клиента для админа."""
    app.dependency_overrides[get_current_user] = lambda: admin
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac
