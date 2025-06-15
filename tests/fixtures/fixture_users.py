"""Модуль создания фикстур для пользователей."""

import pytest

from fastapi.testclient import TestClient

from app.core.user import get_hashed_password, get_current_user
from app.main import app
from app.models import User, RoleEnum


@pytest.fixture
def customer():
    """Фикстура для создания покупателя."""
    return User(
        first_name='admin',
        last_name='admin',
        username='admin',
        email='admin@yandex.ru',
        password=get_hashed_password('password12345'),
        role=RoleEnum.CUSTOMER
    )


@pytest.fixture
def supplier_1():
    """Фикстура для создания поставщика."""
    return User(
        first_name='supplier_1',
        last_name='supplier_1',
        username='supplier_1',
        email='supplier_1@yandex.ru',
        password=get_hashed_password('password12345'),
        role=RoleEnum.SUPPLIER
    )


@pytest.fixture
def supplier_2():
    """Фикстура для создания поставщика."""
    return User(
        first_name='supplier_2',
        last_name='supplier_2',
        username='supplier_2',
        email='supplier_2@yandex.ru',
        password=get_hashed_password('password12345'),
        role=RoleEnum.SUPPLIER
    )


@pytest.fixture
def admin():
    """Фикстура для создания админа."""
    return User(
        first_name='admin',
        last_name='admin',
        username='admin',
        email='admin@yandex.ru',
        password=get_hashed_password('password12345'),
        role=RoleEnum.ADMIN
    )


@pytest.fixture
def customer_client(customer):
    """Фикстура создания клиента для покупателя."""
    app.dependency_overrides[get_current_user] = lambda: customer
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def supplier_1_client(supplier_1):
    """Фикстура создания клиента для поставщика товаров."""
    app.dependency_overrides[get_current_user] = lambda: supplier_1
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def supplier_2_client(supplier_2):
    """Фикстура создания клиента для другого поставщика товаров."""
    app.dependency_overrides[get_current_user] = lambda: supplier_2
    with TestClient(app) as client:
        yield client



@pytest.fixture
def admin_client(admin):
    """Фикстура создания клиента для админа."""
    app.dependency_overrides[get_current_user] = lambda: admin
    with TestClient(app) as client:
        yield client
