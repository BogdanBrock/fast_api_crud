"""Модуль создания тестов для продуктов."""

from http import HTTPStatus

import pytest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pytest_lazy_fixtures import lf
from fastapi.testclient import TestClient

from app.models import Product, User
from .utils import check_json_data, check_db_data, check_db_fields
from .fixtures.fixture_products import LIST_URL, DETAIL_URL


def test_anon_user_can_get_products(client: TestClient):
    """Тест для получения продуктов всеми пользователями."""
    response = client.get(LIST_URL)
    assert response.status_code == HTTPStatus.OK


def test_anon_user_can_get_product(client: TestClient, product_1: Product):
    """Тест для получения продукта всеми пользователями."""
    response = client.get(DETAIL_URL.format(slug=product_1.slug))
    assert response.status_code == HTTPStatus.OK


def test_product_not_found(client: TestClient):
    """Тест для проверки отсутствия продукта"""
    response = client.get(DETAIL_URL.format(slug='product'))
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'parametrized_client, user',
    (
        (lf('supplier_1_client'), lf('supplier_1')),
        (lf('admin_client'), lf('admin'))
    )
)
async def test_admin_or_supplier_can_create_product(
    parametrized_client: TestClient,
    test_db_session: AsyncSession,
    user: User,
    product_request: dict,
    product_response: dict
):
    """Тест для создания продукта поставщиком и администратором."""
    response = parametrized_client.post(LIST_URL, json=product_request)
    assert response.status_code == HTTPStatus.CREATED
    products = (await test_db_session.scalars(select(Product))).all()
    assert len(products) == 1
    product_response['user_username'] = user.username
    check_json_data(response, product_response)
    product_1 = products[0]
    check_db_data(response, product_response, product_1)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('client'), HTTPStatus.UNAUTHORIZED),
        (lf('customer_client'), HTTPStatus.FORBIDDEN)
    )
)
async def test_another_users_cant_create_product(
    parametrized_client: TestClient,
    test_db_session: AsyncSession,
    expected_status: int,
    product_request: dict
):
    """Тест для создания продукта анонимным пользователем и покупателем."""
    response = parametrized_client.post(LIST_URL, json=product_request)
    assert response.status_code == expected_status
    count = await test_db_session.scalar(
        select(func.count()).select_from(Product)
    )
    assert count == 0


@pytest.mark.parametrize(
    'parametrized_client',
    (lf('supplier_1_client'), lf('admin_client'))
)
async def test_supplier_or_admin_can_update_product(
    parametrized_client: TestClient,
    product_request: dict,
    product_response: dict,
    product_1: Product
):
    """Тест для обновления продукта поставщиком и администратором."""
    response = parametrized_client.patch(
        DETAIL_URL.format(slug=product_1.slug),
        json=product_request
    )
    assert response.status_code == HTTPStatus.OK
    check_json_data(response, product_response)
    check_db_data(response, product_response, product_1)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('client'), HTTPStatus.UNAUTHORIZED),
        (lf('customer_client'), HTTPStatus.FORBIDDEN),
        (lf('supplier_2_client'), HTTPStatus.FORBIDDEN)
    )
)
def test_another_users_cant_update_product(
    parametrized_client: TestClient,
    expected_status: int,
    product_request: dict,
    product_1: Product,
    product_fields: tuple[str, ...]
):
    """."""
    response = parametrized_client.patch(
        DETAIL_URL.format(slug=product_1.slug),
        json=product_request
    )
    assert response.status_code == expected_status
    expected_data = {key: getattr(product_1, key) for key in product_fields}
    check_db_data(response, expected_data, product_1)


@pytest.mark.parametrize(
    'parametrized_client',
    (lf('supplier_1_client'), lf('admin_client'))
)
async def test_supplier_or_admin_delete_product(
    parametrized_client: TestClient,
    test_db_session: AsyncSession,
    product_1: Product
):
    """Тест для удаления продукта поставщиком и администратором."""
    response = parametrized_client.delete(
        DETAIL_URL.format(slug=product_1.slug)
    )
    assert response.status_code == HTTPStatus.NO_CONTENT
    count = await test_db_session.scalar(
        select(func.count()).select_from(Product)
    )
    assert count == 0


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('client'), HTTPStatus.UNAUTHORIZED),
        (lf('customer_client'), HTTPStatus.FORBIDDEN),
        (lf('supplier_2_client'), HTTPStatus.FORBIDDEN)
    )
)
async def test_another_users_cant_delete_product(
    parametrized_client: TestClient,
    test_db_session: AsyncSession,
    expected_status: int,
    product_1: Product
):
    """Тест для удаления продукта анонимным пользователем и покупателем."""
    response = parametrized_client.delete(
        DETAIL_URL.format(slug=product_1.slug)
    )
    assert response.status_code == expected_status
    count = await test_db_session.scalar(
        select(func.count()).select_from(Product)
    )
    assert count == 1


def test_model_product(product_fields: tuple[str, ...]):
    """Тест для модели продукта."""
    check_db_fields(product_fields, Product)
