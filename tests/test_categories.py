"""Модуль создания тестов для категорий."""

from http import HTTPStatus

import pytest
from pytest_lazy_fixtures import lf
from slugify import slugify
from sqlalchemy import select, func
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category
from .utils import check_json_data, check_db_data, check_db_fields


class TestCategoryAPI:
    """Класс для тестирования API пользователей."""

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
        """Тест для получения категорий анонимным пользователем."""
        response = await client.get(self.list_url)
        assert response.status_code == HTTPStatus.OK, response.json()

    @pytest.mark.usefixtures('category_2', 'category_3')
    async def test_anon_user_can_get_categories_by_parent_slug(
        self,
        client: AsyncClient,
        parent_category: Category
    ):
        """Тест для получения категорий по родительской категории."""
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
        """Тест для получения категории анонимным пользователем."""
        response = await client.get(
            self.detail_url.format(slug=category_1.slug)
        )
        assert response.status_code == HTTPStatus.OK, response.json()
        expected_data = {f: getattr(category_1, f) for f in self.expected_data}
        check_json_data(response, expected_data)

    async def test_get_category_not_found(self, client: AsyncClient):
        """Тест для получения отсутствующей категории."""
        response = await client.get(self.detail_url.format(slug='not_found'))
        assert response.status_code == HTTPStatus.NOT_FOUND

    async def test_admin_can_create_category(
        self,
        admin_client: AsyncClient,
        test_db_session: AsyncSession,
        parent_category: Category
    ):
        """Тест для создания категории администратором."""
        request_data = {
            'name': 'категория 10',
            'parent_slug': parent_category.slug
        }
        response = await admin_client.post(self.list_url, json=request_data)
        assert response.status_code == HTTPStatus.CREATED, response.json()
        expected_data = {
            'id': 2,
            'name': request_data['name'],
            'slug': slugify(request_data['name']),
            'parent_slug': request_data['parent_slug']
        }
        check_json_data(response, expected_data)
        categories = (await test_db_session.scalars(select(Category))).all()
        assert len(categories) == 2
        check_db_data(response, expected_data, categories[-1])

    async def test_admin_cant_create_category_with_already_exists_data(
        self,
        admin_client: AsyncClient,
        test_db_session: AsyncSession,
        category_1: Category
    ):
        """Тест для создания уже существующей категории."""
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
    async def test_another_user_cant_create_category(
        self,
        user_client: AsyncClient,
        test_db_session: AsyncSession,
        expected_status: int
    ):
        """Тест для создания категории анонимным пользователем, покупателем и поставщиком товаром."""
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
        """Тест для изменения категории администратором."""
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
        """Тест для изменения категории администратором на уже существующие данные."""
        expected_data = {'name': category_1.name, 'slug': category_1.slug}
        response = await admin_client.patch(
            self.detail_url.format(slug=category_1.slug),
            json={'name': category_2.name}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        check_db_data(response, expected_data, category_1)

    async def test_admin_cant_patch_parent_slug_on_other_value(
        self,
        admin_client: AsyncClient,
        parent_category: Category,
        category_1: Category
    ):
        parent_slug = category_1.parent_slug
        response = await admin_client.patch(
            self.detail_url.format(slug=category_1.slug),
            json={'parent_slug': parent_category.slug}
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()['parent_slug'] == parent_slug
        assert category_1.parent_slug == parent_slug

    async def test_patch_category_not_found(self, admin_client: AsyncClient):
        """Тест для изменения несуществующей категории администратором."""
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
    async def test_another_user_cant_patch_category(
        self,
        user_client: AsyncClient,
        expected_status: int,
        parent_category: Category,
    ):
        """Тест для изменения категории анонимым пользователем, покупателем и поставщиком товаров."""
        response = await user_client.patch(
            self.detail_url.format(slug=parent_category.slug),
            json=self.request_data
        )
        assert response.status_code == expected_status
        expected_data = {
            f: getattr(parent_category, f) for f in self.expected_data
        }
        check_db_data(response, expected_data, parent_category)

    @pytest.mark.parametrize(
        'parametrized_client, expected_status, expected_count',
        (
            (lf('client'), HTTPStatus.UNAUTHORIZED, 1),
            (lf('customer_client'), HTTPStatus.FORBIDDEN, 1),
            (lf('supplier_1_client'), HTTPStatus.FORBIDDEN, 1),
            (lf('admin_client'), HTTPStatus.NO_CONTENT, 0)
        ),
        ids=('anon_user', 'customer', 'supplier', 'admin')
    )
    async def test_delete_category(
        self,
        parametrized_client: AsyncClient,
        expected_status: int,
        expected_count: int,
        test_db_session: AsyncSession,
        parent_category: Category
    ):
        """Тест для удалении категории всеми пользователями."""
        response = await parametrized_client.delete(
            self.detail_url.format(slug=parent_category.slug)
        )
        assert response.status_code == expected_status
        count = await test_db_session.scalar(
            select(func.count()).select_from(Category)
        )
        assert count == expected_count

    async def test_delete_category_not_found(self, admin_client: AsyncClient):
        """Тест для удаления несуществующей категории администратором."""
        response = await admin_client.delete(
            self.detail_url.format(slug='not_found')
        )
        assert response.status_code == HTTPStatus.NOT_FOUND


class TestCategoryModel:
    """Класс для тестирования модели Category."""

    def test_model_fields(self):
        """Тест для проверки наличия полей модели категории."""
        category_fields = ('id', 'name', 'slug', 'parent_slug')
        check_db_fields(category_fields, Category)
