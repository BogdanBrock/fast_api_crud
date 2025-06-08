"""Модуль создания тестов для категорий."""

from http import HTTPStatus
from httpx import AsyncClient

import pytest
from pytest_lazy_fixtures import lf
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

from app.models import Category
from .utils import check_json_data, check_db_data, check_db_fields
from .fixtures.categories import LIST_URL, DETAIL_URL


@pytest.mark.parametrize(
    'parametrized_client',
    (
        lf('client'),
        lf('customer_client'),
        lf('supplier_client'),
        lf('admin_client')
    )
)
def test_anon_user_can_get_categories(parametrized_client: TestClient) -> None:
    """Тест для получения категорий всеми пользователями."""
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
def test_anon_user_can_get_category(
    parametrized_client: TestClient,
    category: Category
) -> None:
    """Тест для получения категории всеми пользователями."""
    response = parametrized_client.get(DETAIL_URL.format(slug=category.slug))
    assert response.status_code == HTTPStatus.OK


async def test_admin_can_create_category(
    admin_client: TestClient,
    test_db_session: AsyncSession,
    category_request: dict,
    category_response: dict
) -> None:
    """Тест для создания категории администратором."""
    response = admin_client.post(LIST_URL, json=category_request)
    assert response.status_code == HTTPStatus.CREATED
    categories = (await test_db_session.scalars(select(Category))).all()
    assert len(categories) == 1
    check_json_data(response, category_response)
    category = categories[0]
    check_db_data(response, category_response, category)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('client'), HTTPStatus.UNAUTHORIZED),
        (lf('customer_client'), HTTPStatus.FORBIDDEN),
        (lf('supplier_client'), HTTPStatus.FORBIDDEN)
    )
)
async def test_another_users_cant_create_category(
    parametrized_client: TestClient,
    expected_status: int,
    test_db_session: AsyncSession,
    category_request: dict
) -> None:
    """
    Тест для создания категории анонимным
    пользователем, покупателем и поставщиком товаром.
    """
    response = parametrized_client.post(LIST_URL, json=category_request)
    assert response.status_code == expected_status
    count = await test_db_session.scalar(
        select(func.count()).select_from(Category)
    )
    assert count == 0


def test_admin_can_update_category(
    admin_client: TestClient,
    category: Category,
    category_request: dict,
    category_response: dict
) -> None:
    """Тест для изменения категории администратором."""
    response = admin_client.patch(
        DETAIL_URL.format(slug=category.slug),
        json=category_request
    )
    assert response.status_code == HTTPStatus.OK
    check_json_data(response, category_response)
    check_db_data(response, category_response, category)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('client'), HTTPStatus.UNAUTHORIZED),
        (lf('customer_client'), HTTPStatus.FORBIDDEN),
        (lf('supplier_client'), HTTPStatus.FORBIDDEN)
    )
)
def test_another_user_cant_update_category(
    parametrized_client: TestClient,
    expected_status: int,
    category: Category,
    category_request: dict,
    category_fields: tuple[str, ...]
) -> None:
    """
    Тест для изменения категории анонимым
    пользователем, покупателем и поставщиком товаров.
    """
    response = parametrized_client.patch(
        DETAIL_URL.format(slug=category.slug),
        json=category_request
    )
    assert response.status_code == expected_status
    expected_data = {key: getattr(category, key) for key in category_fields}
    check_db_data(response, expected_data, category)


@pytest.mark.parametrize(
    'parametrized_client, expected_status, expected_count',
    (
        (lf('client'), HTTPStatus.UNAUTHORIZED, 1),
        (lf('customer_client'), HTTPStatus.FORBIDDEN, 1),
        (lf('supplier_client'), HTTPStatus.FORBIDDEN, 1),
        (lf('admin_client'), HTTPStatus.NO_CONTENT, 0)
    )
)
async def test_users_delete_category(
    parametrized_client: TestClient,
    expected_status: int,
    expected_count: int,
    test_db_session: AsyncSession,
    category: Category
) -> None:
    """Тест для удалении категории всеми пользователями."""
    response = parametrized_client.delete(
        DETAIL_URL.format(slug=category.slug)
    )
    assert response.status_code == expected_status
    count = await test_db_session.scalar(
        select(func.count()).select_from(Category)
    )
    assert count == expected_count


def test_model_category(category_fields: tuple[str, ...]) -> None:
    """Тест для модели категории."""
    check_db_fields(category_fields, Category)
