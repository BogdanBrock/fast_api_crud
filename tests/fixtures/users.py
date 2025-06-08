"""Модуль создания фикстур для пользователей."""

import pytest
import pytest_asyncio

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, RoleEnum
from app.core.user import get_hashed_password, get_current_user

from app.main import app
from ..utils import create_db_obj

customer_data = dict(
    first_name='admin',
    last_name='admin',
    username='admin',
    email='admin@yandex.ru',
    password=get_hashed_password('password12345'),
    role=RoleEnum.CUSTOMER
)

supplier_data = dict(
    first_name='supplier',
    last_name='supplier',
    username='supplier',
    email='supplier@yandex.ru',
    password=get_hashed_password('password12345'),
    role=RoleEnum.SUPPLIER
)

admin_data = dict(
    first_name='admin',
    last_name='admin',
    username='admin',
    email='admin@yandex.ru',
    password=get_hashed_password('password12345'),
    role=RoleEnum.ADMIN
)


@pytest_asyncio.fixture
async def customer(test_db_session):
    return await create_db_obj(test_db_session, User(**customer_data))


@pytest_asyncio.fixture
async def supplier(test_db_session):
    return await create_db_obj(test_db_session, User(**supplier_data))


@pytest_asyncio.fixture
async def admin(test_db_session):
    return await create_db_obj(test_db_session, User(**admin_data))


@pytest.fixture
def client():
    """Фикстура для создания анонимного клиента."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def customer_client():
    """Фикстура создания клиента для покупателя."""
    app.dependency_overrides[get_current_user] = lambda: User(**customer_data)
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def supplier_client(supplier):
    """Фикстура создания клиента для поставщика товаров."""
    app.dependency_overrides[get_current_user] = lambda: User(**supplier_data)
    with TestClient(app) as client:
        yield client


@pytest.fixture
def admin_client():
    """Фикстура создания клиента для админа."""
    app.dependency_overrides[get_current_user] = lambda: User(**admin_data)
    with TestClient(app) as client:
        yield client
