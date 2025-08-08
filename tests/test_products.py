"""Модуль создания тестов для продуктов."""

from decimal import Decimal
from http import HTTPStatus
from typing import Any

import pytest
from httpx import AsyncClient
from pytest_lazy_fixtures import lf
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product, Review, User
from .utils import check_db_data, check_db_fields, check_json_data


class TestProductAPI:
    """Класс для тестирования API продукта."""

    list_url = '/api/v1/products/'
    detail_url = list_url + '{slug}/'

    async def test_anon_user_can_get_products(self, client: AsyncClient):
        """Тест для проверки получения продуктов анонимным пользователем."""
        response = await client.get(self.list_url)
        assert response.status_code == HTTPStatus.OK

    async def test_anon_user_can_get_product(
        self,
        client: AsyncClient,
        product_1: Product,
        product_fields: tuple[str, ...]
    ):
        """Тест для проверки получения продукта анонимным пользователем."""
        response = await client.get(
            self.detail_url.format(slug=product_1.slug)
        )
        assert response.status_code == HTTPStatus.OK
        expected_data = {f: getattr(product_1, f) for f in product_fields}
        check_json_data(response, expected_data)

    async def test_product_not_found_for_getting(self, client: AsyncClient):
        """
        Тест для проверки наличия ошибки 404
        при получении несуществующего продукта.
        """
        response = await client.get(self.detail_url.format(slug='product'))
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize(
        'parametrized_client, user',
        (
            (lf('supplier_1_client'), lf('supplier_1')),
            (lf('admin_client'), lf('admin'))
        ),
        ids=('supplier', 'admin')
    )
    async def test_admin_or_supplier_can_create_product(
        self,
        parametrized_client: AsyncClient,
        test_db_session: AsyncSession,
        user: User,
        product_request_data: dict[str, Any],
        product_response_data: dict[str, Any],
    ):
        """
        Тест для проверки создания продукта поставщиком или администратором.
        """
        response = await parametrized_client.post(
            self.list_url, json=product_request_data
        )
        assert response.status_code == HTTPStatus.CREATED
        products = (await test_db_session.scalars(select(Product))).all()
        assert len(products) == 1
        product_response_data['user_username'] = user.username
        check_json_data(response, product_response_data)
        product_1 = products[0]
        check_db_data(response, product_response_data, product_1)

    @pytest.mark.parametrize(
        'parametrized_client, expected_status',
        (
            (lf('client'), HTTPStatus.UNAUTHORIZED),
            (lf('customer_client'), HTTPStatus.FORBIDDEN)
        )
    )
    async def test_anon_user_or_customer_cant_create_product(
        self,
        parametrized_client: AsyncClient,
        test_db_session: AsyncSession,
        expected_status: int,
        product_request_data: dict[str, Any]
    ):
        """
        Тест для проверки невозможности создания продукта
        анонимным пользователем или покупателем.
        """
        response = await parametrized_client.post(
            self.list_url, json=product_request_data
        )
        assert response.status_code == expected_status
        count = await test_db_session.scalar(
            select(func.count()).select_from(Product)
        )
        assert count == 0

    @pytest.mark.parametrize(
        'parametrized_client',
        (lf('supplier_1_client'), lf('admin_client'))
    )
    async def test_supplier_or_admin_can_patch_product(
        self,
        parametrized_client: AsyncClient,
        product_request_data: dict[str, Any],
        product_response_data: dict[str, Any],
        product_1: Product
    ):
        """
        Тест для проверки изменения продукта
        поставщиком или администратором.
        """
        response = await parametrized_client.patch(
            self.detail_url.format(slug=product_1.slug),
            json=product_request_data
        )
        assert response.status_code == HTTPStatus.OK
        check_json_data(response, product_response_data)
        check_db_data(response, product_response_data, product_1)

    async def test_product_not_found_for_patching(
        self,
        supplier_1_client: AsyncClient,
        product_request_data: dict[str, Any]
    ):
        """
        Тест для проверки наличия ошибки 404
        при изменении несуществующего продукта.
        """
        response = await supplier_1_client.patch(
            self.detail_url.format(slug='product'), json=product_request_data
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize(
        'parametrized_client, expected_status',
        (
            (lf('client'), HTTPStatus.UNAUTHORIZED),
            (lf('customer_client'), HTTPStatus.FORBIDDEN)
        ),
        ids=('anon_user', 'customer')
    )
    async def test_anon_user_or_customer_cant_patch_product(
        self,
        parametrized_client: AsyncClient,
        expected_status: int,
        product_request_data: dict[str, Any],
        product_1: Product,
        product_fields: tuple[str, ...]
    ):
        """
        Тест для проверки невозможности изменения
        продукта анонимным пользователем или покупателем.
        """
        response = await parametrized_client.patch(
            self.detail_url.format(slug=product_1.slug),
            json=product_request_data
        )
        assert response.status_code == expected_status
        expected_data = {
            key: getattr(product_1, key) for key in product_fields
        }
        check_db_data(response, expected_data, product_1)

    async def test_supplier_cant_patch_other_product(
        self,
        supplier_2_client: AsyncClient,
        product_request_data: dict[str, Any],
        product_1: Product,
        product_fields: tuple[str, ...]
    ):
        """
        Тест для проверки невозможности
        изменения чужого продукта поставщиком.
        """
        response = await supplier_2_client.patch(
            self.detail_url.format(slug=product_1.slug),
            json=product_request_data
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
        expected_data = {
            key: getattr(product_1, key) for key in product_fields
        }
        check_db_data(response, expected_data, product_1)

    @pytest.mark.parametrize(
        'parametrized_client',
        (lf('supplier_1_client'), lf('admin_client'))
    )
    async def test_supplier_or_admin_can_delete_product(
        self,
        parametrized_client: AsyncClient,
        test_db_session: AsyncSession,
        product_1: Product
    ):
        """
        Тест для проверки удаления продукта
        поставщиком или администратором.
        """
        response = await parametrized_client.delete(
            self.detail_url.format(slug=product_1.slug)
        )
        assert response.status_code == HTTPStatus.NO_CONTENT
        count = await test_db_session.scalar(
            select(func.count()).select_from(Product)
        )
        assert count == 0

    async def test_product_not_found_for_deleting(
        self,
        supplier_1_client: AsyncClient
    ):
        """
        Тест для проверки наличия ошибки 404
        при удалении несуществующего продукта.
        """
        response = await supplier_1_client.delete(
            self.detail_url.format(slug='product')
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize(
        'parametrized_client, expected_status',
        (
            (lf('client'), HTTPStatus.UNAUTHORIZED),
            (lf('customer_client'), HTTPStatus.FORBIDDEN)
        )
    )
    async def test_anon_user_or_customer_cant_delete_product(
        self,
        parametrized_client: AsyncClient,
        test_db_session: AsyncSession,
        expected_status: int,
        product_1: Product
    ):
        """
        Тест для проверки невозможности удаления продукта
        анонимным пользователем или покупателем.
        """
        response = await parametrized_client.delete(
            self.detail_url.format(slug=product_1.slug)
        )
        assert response.status_code == expected_status
        count = await test_db_session.scalar(
            select(func.count()).select_from(Product)
        )
        assert count == 1

    async def test_supplier_cant_delete_other_product(
        self,
        supplier_2_client: AsyncClient,
        test_db_session: AsyncSession,
        product_1: Product
    ):
        """
        Тест для проверки невозможности
        удаления чужого продукта поставщиком.
        """
        response = await supplier_2_client.delete(
            self.detail_url.format(slug=product_1.slug)
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
        count = await test_db_session.scalar(
            select(func.count()).select_from(Product)
        )
        assert count == 1


class TestProductModel:
    """Класс для тестирования модели продукта."""

    def test_model_product_fields(self, product_fields: tuple[str, ...]):
        """Тест для проверки наличия ождиаемых полей для модели продукта."""
        check_db_fields(product_fields, Product)

    async def test_product_has_average_grade(
        self,
        test_db_session: AsyncSession,
        product_1: Product,
        review_1: Review,
        review_3: Review
    ):
        """Тест для проверки получения средней оценки продукта."""
        await test_db_session.refresh(product_1)
        grade_1 = Decimal(str(review_1.grade))
        grade_2 = Decimal(str(review_3.grade))
        assert product_1.rating == (grade_1 + grade_2) / Decimal(str(2))
