"""Модуль создания тестов для категорий."""

from http import HTTPStatus

import pytest
from httpx import AsyncClient
from pytest_lazy_fixtures import lf
from slugify import slugify
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category
from .utils import check_db_data, check_db_fields, check_json_data


class TestCategoryAPI:
    """Класс для тестирования API категории."""

    list_url = '/api/v1/categories/'
    detail_url = '/api/v1/categories/{slug}/'

    request_data = {'name': 'категория 1'}
    expected_data = {
        'id': 1,
        'name': request_data['name'],
        'slug': slugify(request_data['name']),
        'parent_slug': None
    }

    async def test_anon_user_can_get_categories(self, client: AsyncClient):
        """Тест для проверки получения категорий анонимным пользователем."""
        response = await client.get(self.list_url)
        assert response.status_code == HTTPStatus.OK, response.json()

    @pytest.mark.usefixtures('category_2', 'category_3')
    async def test_anon_user_can_get_categories_by_parent_category(
        self,
        client: AsyncClient,
        parent_category: Category
    ):
        """
        Тест для проверки получения категорий по
        родительской категории анонимным пользователем.
        """
        params = {'parent_slug': parent_category.slug}
        response = await client.get(self.list_url, params=params)
        data = response.json()
        assert response.status_code == HTTPStatus.OK, data
        assert len(data) == 2

    async def test_anon_user_can_get_category(
        self,
        client: AsyncClient,
        category_1: Category
    ):
        """Тест для проверки получения категории анонимным пользователем."""
        response = await client.get(
            self.detail_url.format(slug=category_1.slug)
        )
        assert response.status_code == HTTPStatus.OK, response.json()
        expected_data = {f: getattr(category_1, f) for f in self.expected_data}
        check_json_data(response, expected_data)

    async def test_category_not_found_for_getting(self, client: AsyncClient):
        """
        Тест для проверки наличия ошибки 404
        при получении несуществующей категории.
        """
        response = await client.get(self.detail_url.format(slug='not_found'))
        assert response.status_code == HTTPStatus.NOT_FOUND

    async def test_admin_can_create_category(
        self,
        admin_client: AsyncClient,
        test_db_session: AsyncSession
    ):
        """Тест для проверки создания категории администратором."""
        response = await admin_client.post(
            self.list_url, json=self.request_data
        )
        assert response.status_code == HTTPStatus.CREATED, response.json()
        check_json_data(response, self.expected_data)
        categories = (await test_db_session.scalars(select(Category))).all()
        assert len(categories) == 1
        check_db_data(response, self.expected_data, categories[-1])

    async def test_admin_cant_create_category_with_already_exists_data(
        self,
        admin_client: AsyncClient,
        test_db_session: AsyncSession,
        category_1: Category
    ):
        """Тест для проверки невозможности
        создания уже существующей категории.
        """
        response = await admin_client.post(
            self.list_url,
            json={'name': category_1.name}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        count = await test_db_session.scalar(
            select(func.count()).select_from(Category)
        )
        assert count == 1

    @pytest.mark.parametrize(
        'user_client, expected_status',
        (
            (lf('client'), HTTPStatus.UNAUTHORIZED),
            (lf('customer_client'), HTTPStatus.FORBIDDEN),
            (lf('supplier_1_client'), HTTPStatus.FORBIDDEN)
        ),
        ids=('anon_user', 'customer', 'supplier')
    )
    async def test_another_users_cant_create_category(
        self,
        user_client: AsyncClient,
        test_db_session: AsyncSession,
        expected_status: int
    ):
        """
        Тест для проверки невозможности создания
        категории другими пользователями.
        """
        response = await user_client.post(
            self.list_url,
            json=self.request_data
        )
        assert response.status_code == expected_status
        count = await test_db_session.scalar(
            select(func.count()).select_from(Category)
        )
        assert count == 0

    async def test_admin_can_patch_category(
        self,
        admin_client: AsyncClient,
        category_1: Category,
    ):
        """Тест для проверки изменения категории администратором."""
        response = await admin_client.patch(
            self.detail_url.format(slug=category_1.slug),
            json=self.request_data
        )
        assert response.status_code == HTTPStatus.OK, response.json()
        check_json_data(response, self.expected_data)
        check_db_data(response, self.expected_data, category_1)

    async def test_admin_cant_patch_category_on_already_exists_data(
        self,
        admin_client: AsyncClient,
        category_1: Category,
        category_2: Category
    ):
        """
        Тест для проверки невозможности изменения категории
        администратором на уже существующие данные.
        """
        expected_data = {'name': category_1.name, 'slug': category_1.slug}
        response = await admin_client.patch(
            self.detail_url.format(slug=category_1.slug),
            json={'name': category_2.name}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        check_db_data(response, expected_data, category_1)

    @pytest.mark.usefixtures('category_2')
    async def test_admin_cant_patch_parent_category(
        self,
        admin_client: AsyncClient,
        parent_category: Category
    ):
        """Тест для проверки невозможности изменения родительской категории."""
        expected_data = {
            'name': parent_category.name,
            'slug': parent_category.slug
        }
        slug = parent_category.slug
        response = await admin_client.patch(
            self.detail_url.format(slug=slug),
            json={'name': 'Другая категория'}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        check_db_data(response, expected_data, parent_category)

    async def test_category_not_found_for_pathcing(
        self,
        admin_client: AsyncClient
    ):
        """
        Тест для проверки наличия ошибки 404
        при изменении несуществующей категории.
        """
        response = await admin_client.patch(
            self.detail_url.format(slug='not_found'),
            json=self.request_data
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize(
        'user_client, expected_status',
        (
            (lf('client'), HTTPStatus.UNAUTHORIZED),
            (lf('customer_client'), HTTPStatus.FORBIDDEN),
            (lf('supplier_1_client'), HTTPStatus.FORBIDDEN)
        ),
        ids=('anon_user', 'customer', 'supplier')
    )
    async def test_another_users_cant_patch_category(
        self,
        user_client: AsyncClient,
        expected_status: int,
        parent_category: Category,
    ):
        """
        Тест для проверки невозможности изменения
        категории другими пользователями.
        """
        response = await user_client.patch(
            self.detail_url.format(slug=parent_category.slug),
            json=self.request_data
        )
        assert response.status_code == expected_status
        expected_data = {
            f: getattr(parent_category, f) for f in self.expected_data
        }
        check_db_data(response, expected_data, parent_category)

    async def test_admin_can_delete_category(
        self,
        admin_client,
        test_db_session: AsyncSession,
        parent_category: Category
    ):
        """Тест для проверки удаления категории администратором."""
        response = await admin_client.delete(
            self.detail_url.format(slug=parent_category.slug)
        )
        assert response.status_code == HTTPStatus.NO_CONTENT
        count = await test_db_session.scalar(
            select(func.count()).select_from(Category)
        )
        assert count == 0

    @pytest.mark.parametrize(
        'parametrized_client, expected_status',
        (
            (lf('client'), HTTPStatus.UNAUTHORIZED),
            (lf('customer_client'), HTTPStatus.FORBIDDEN),
            (lf('supplier_1_client'), HTTPStatus.FORBIDDEN)
        ),
        ids=('anon_user', 'customer', 'supplier')
    )
    async def test_another_users_cant_delete_category(
        self,
        parametrized_client: AsyncClient,
        expected_status: int,
        test_db_session: AsyncSession,
        parent_category: Category
    ):
        """Тест для проверки невозможности
        удаления категории другими пользователями."""
        response = await parametrized_client.delete(
            self.detail_url.format(slug=parent_category.slug)
        )
        assert response.status_code == expected_status
        count = await test_db_session.scalar(
            select(func.count()).select_from(Category)
        )
        assert count == 1

    async def test_category_not_found_for_deleting(
        self,
        admin_client: AsyncClient
    ):
        """
        Тест для проверки невозможности удаления
        несуществующей категории администратором.
        """
        response = await admin_client.delete(
            self.detail_url.format(slug='not_found')
        )
        assert response.status_code == HTTPStatus.NOT_FOUND


class TestCategoryModel:
    """Класс для тестирования модели Category."""

    def test_model_category_fields(self):
        """Тест для проверки наличия ожидаемых полей для модели категории."""
        category_fields = ('id', 'name', 'slug', 'parent_slug')
        check_db_fields(category_fields, Category)
