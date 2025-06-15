"""Модуль создания тестов для категорий."""

from http import HTTPStatus

import pytest
from pytest_lazy_fixtures import lf
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

from app.models import Category
from .utils import check_json_data, check_db_data, check_db_fields
from .fixtures.fixture_categories import LIST_URL, DETAIL_URL


def test_anon_user_can_get_categories(client: TestClient):
    """Тест для получения категории для анонимного пользователя."""
    response = client.get(LIST_URL)
    assert response.status_code == HTTPStatus.OK, response.json()


@pytest.mark.usefixtures('category_1', 'category_2')
async def test_anon_user_can_get_categories_by_parent_slug(
    client: TestClient,
    parent_category: Category
):
    """Тест для получения категорий по родительской категории."""
    params = {'parent_slug': parent_category.slug}
    response = client.get(LIST_URL, params=params)
    data = response.json()
    assert response.status_code == HTTPStatus.OK, response.json()
    assert len(data) == 2


def test_anon_user_can_get_category(
    client: TestClient,
    parent_category: Category
):
    """Тест для получения категории для анонимного пользователя."""
    response = client.get(DETAIL_URL.format(slug=parent_category.slug))
    assert response.status_code == HTTPStatus.OK, response.json()


def test_category_not_found(client: TestClient):
    """Тест для проверки отсутствия категории."""
    response = client.get(DETAIL_URL.format(slug='category'))
    assert response.status_code == HTTPStatus.NOT_FOUND


async def test_admin_can_create_category(
    admin_client: TestClient,
    test_db_session: AsyncSession,
    category_request: dict,
    category_response: dict
):
    """Тест для создания категории администратором."""
    response = admin_client.post(LIST_URL, json=category_request)
    assert response.status_code == HTTPStatus.CREATED, response.json()
    categories = (await test_db_session.scalars(select(Category))).all()
    assert len(categories) == 1
    check_json_data(response, category_response)
    category = categories[0]
    check_db_data(response, category_response, category)


@pytest.mark.usefixtures('parent_category')
async def test_admin_cant_create_category_one_more(
    admin_client: TestClient,
    test_db_session: AsyncSession,
    category_request: dict
):
    """Тест для создания уже существующей категории."""
    response = admin_client.post(LIST_URL, json=category_request)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    count = await test_db_session.scalar(
        select(func.count()).select_from(Category)
    )
    assert count == 1


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('client'), HTTPStatus.UNAUTHORIZED),
        (lf('customer_client'), HTTPStatus.FORBIDDEN),
        (lf('supplier_1_client'), HTTPStatus.FORBIDDEN)
    )
)
async def test_another_users_cant_create_category(
    parametrized_client: TestClient,
    expected_status: int,
    test_db_session: AsyncSession,
    category_request: dict
):
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
    parent_category: Category,
    category_request: dict,
    category_response: dict
):
    """Тест для изменения категории администратором."""
    response = admin_client.patch(
        DETAIL_URL.format(slug=parent_category.slug),
        json=category_request
    )
    assert response.status_code == HTTPStatus.OK, response.json()
    check_json_data(response, category_response)
    check_db_data(response, category_response, parent_category)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('client'), HTTPStatus.UNAUTHORIZED),
        (lf('customer_client'), HTTPStatus.FORBIDDEN),
        (lf('supplier_1_client'), HTTPStatus.FORBIDDEN)
    )
)
def test_another_user_cant_update_category(
    parametrized_client: TestClient,
    expected_status: int,
    parent_category: Category,
    category_request: dict,
    category_fields: tuple[str, ...]
):
    """
    Тест для изменения категории анонимым
    пользователем, покупателем и поставщиком товаров.
    """
    response = parametrized_client.patch(
        DETAIL_URL.format(slug=parent_category.slug),
        json=category_request
    )
    assert response.status_code == expected_status
    expected_data = {f: getattr(parent_category, f) for f in category_fields}
    check_db_data(response, expected_data, parent_category)


@pytest.mark.parametrize(
    'parametrized_client, expected_status, expected_count',
    (
        (lf('client'), HTTPStatus.UNAUTHORIZED, 1),
        (lf('customer_client'), HTTPStatus.FORBIDDEN, 1),
        (lf('supplier_1_client'), HTTPStatus.FORBIDDEN, 1),
        (lf('admin_client'), HTTPStatus.NO_CONTENT, 0)
    )
)
async def test_users_delete_category(
    parametrized_client: TestClient,
    expected_status: int,
    expected_count: int,
    test_db_session: AsyncSession,
    parent_category: Category
):
    """Тест для удалении категории всеми пользователями."""
    response = parametrized_client.delete(
        DETAIL_URL.format(slug=parent_category.slug)
    )
    assert response.status_code == expected_status
    count = await test_db_session.scalar(
        select(func.count()).select_from(Category)
    )
    assert count == expected_count


def test_model_category(category_fields: tuple[str, ...]) -> None:
    """Тест для проверки наличия полей модели категории."""
    check_db_fields(category_fields, Category)
