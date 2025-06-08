"""Модуль создания тестов для продуктов."""

from http import HTTPStatus

import pytest
import pytest_asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pytest_lazy_fixtures import lf
from fastapi.testclient import TestClient

from app.models import Product, User
from .utils import check_json_data, check_db_data, check_db_fields

from .fixtures.products import LIST_URL, DETAIL_URL


@pytest.mark.parametrize(
    'parametrized_client',
    (
        lf('client'),
        lf('customer_client'),
        lf('supplier_client'),
        lf('admin_client')
    )
)
def test_anon_user_can_get_products(parametrized_client: TestClient) -> None:
    """Тест для получения продуктов всеми пользователями."""
    response = parametrized_client.get(LIST_URL)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client',
    (
        lf('client'),
        lf('customer_client'),
        lf('supplier_client'),
        lf('admin_client')
    )
)
def test_anon_user_can_get_product(
    parametrized_client: TestClient,
    product: Product
) -> None:
    """Тест для получения продукта всеми пользователями."""
    response = parametrized_client.get(DETAIL_URL.format(slug=product.slug))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, user',
    (
        (lf('supplier_client'), lf('supplier')),
        (lf('admin_client'), lf('admin'))
    )
)
async def test_admin_or_supplier_can_create_product(
    parametrized_client: TestClient,
    user: User,
    product_request: dict,
    product_response: dict,
    test_db_session: AsyncSession
) -> None:
    """Тест для создания продукта поставщиком и администратором."""
    response = parametrized_client.post(LIST_URL, json=product_request)
    assert response.status_code == HTTPStatus.CREATED
    products = (await test_db_session.scalars(select(Product))).all()
    assert len(products) == 1
    product_response['user_username'] = await user.awaitable_attrs.username
    check_json_data(response, product_response)
    product = products[0]
    check_db_data(response, product_response, product)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('client'), HTTPStatus.UNAUTHORIZED),
        (lf('customer_client'), HTTPStatus.FORBIDDEN)
    )
)
async def test_another_users_cant_create_product(
    parametrized_client: TestClient,
    expected_status: int,
    product_request: dict,
    test_db_session: AsyncSession
) -> None:
    """Тест для создания продукта анонимным пользователем и покупателем."""
    response = parametrized_client.post(LIST_URL, json=product_request)
    assert response.status_code == expected_status
    count = await test_db_session.scalar(
        select(func.count()).select_from(Product)
    )
    assert count == 0


@pytest.mark.parametrize(
    'parametrized_client',
    (lf('supplier_client'), lf('admin_client'))
)
def test_supplier_or_admin_can_update_product(
    parametrized_client: TestClient,
    product_request: dict,
    product_response: dict,
    product: Product
) -> None:
    """Тест для обновления продукта поставщиком и администратором."""
    response = parametrized_client.patch(
        DETAIL_URL.format(slug=product.slug),
        json=product_request
    )
    assert response.status_code == HTTPStatus.OK
    check_json_data(response, product_response)
    check_db_data(response, product_response, product)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('client'), HTTPStatus.UNAUTHORIZED),
        (lf('customer_client'), HTTPStatus.FORBIDDEN)
    )
)
def test_another_users_cant_update_product(
    parametrized_client: TestClient,
    expected_status: int,
    product_request: dict,
    product: Product,
    product_fields: tuple[str, ...]
) -> None:
    """Тест для обновления продукта анонимным пользователем и покупателем."""
    response = parametrized_client.patch(
        DETAIL_URL.format(slug=product.slug),
        json=product_request
    )
    assert response.status_code == expected_status
    expected_data = {key: getattr(product, key) for key in product_fields}
    check_db_data(response, expected_data, product)


@pytest.mark.parametrize(
    'parametrized_client',
    (lf('supplier_client'), lf('admin_client'))
)
async def test_supplier_or_admin_delete_product(
    parametrized_client: TestClient,
    product: Product,
    test_db_session: AsyncSession
) -> None:
    """Тест для удаления продукта поставщиком и администратором."""
    response = parametrized_client.delete(DETAIL_URL.format(slug=product.slug))
    assert response.status_code == HTTPStatus.NO_CONTENT
    count = await test_db_session.scalar(
        select(func.count()).select_from(Product)
    )
    assert count == 0


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('client'), HTTPStatus.UNAUTHORIZED),
        (lf('customer_client'), HTTPStatus.FORBIDDEN)
    )
)
async def test_another_users_cant_delete_product(
    parametrized_client: TestClient,
    expected_status: int,
    product: Product,
    test_db_session: AsyncSession
) -> None:
    """Тест для удаления продукта анонимным пользователем и покупателем."""
    response = parametrized_client.delete(DETAIL_URL.format(slug=product.slug))
    assert response.status_code == expected_status
    count = await test_db_session.scalar(
        select(func.count()).select_from(Product)
    )
    assert count == 1


def test_model_product(product_fields: tuple[str, ...]):
    """Тест для модели продукта."""
    check_db_fields(product_fields, Product)
