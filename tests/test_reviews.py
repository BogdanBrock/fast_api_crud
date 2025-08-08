"""Модуль создания тестов для отзывов."""

from http import HTTPStatus
from typing import Any

import pytest
from httpx import AsyncClient
from pytest_lazy_fixtures import lf
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product, Review, User
from .utils import check_db_data, check_db_fields, check_json_data


class TestReviewAPI:
    """Класс для тестирования API отзыва."""

    list_url = '/api/v1/products/{slug}/reviews/'
    detail_url = list_url + '{id}/'

    async def test_anon_user_can_get_reviews(self, client: AsyncClient):
        """Тест для проверки получения отзывов анонимным пользователем."""
        response = await client.get('api/v1/reviews/')
        assert response.status_code == HTTPStatus.OK, response.json()

    async def test_anon_user_can_get_review(
        self,
        client: AsyncClient,
        review_1: Review,
        review_fields: tuple[str, ...]
    ):
        """Тест для проверки получения отзыва анонимным пользователем."""
        response = await client.get(
            self.detail_url.format(slug=review_1.product.slug, id=review_1.id)
        )
        assert response.status_code == HTTPStatus.OK, response.json()
        expected_data = {f: getattr(review_1, f) for f in review_fields}
        check_json_data(response, expected_data)

    async def test_review_not_found_for_getting(self, client: AsyncClient):
        """
        Тест для проверки наличия ошибки 404
        при получении несуществующего отзыва.
        """
        response = await client.get(
            self.detail_url.format(slug='product', id=1)
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize(
        'parametrized_client, user',
        (
            (lf('customer_client'), lf('customer')),
            (lf('supplier_1_client'), lf('supplier_1')),
            (lf('admin_client'), lf('admin'))
        ),
        ids=('customer', 'supplier', 'admin')
    )
    async def test_auth_users_can_create_review(
        self,
        parametrized_client: AsyncClient,
        test_db_session: AsyncSession,
        user: User,
        product_2: Product
    ):
        """
        Тест для проверки создания отзыва
        всеми авторизованными пользователями.
        """
        data = {'grade': 5}
        response = await parametrized_client.post(
            self.list_url.format(slug=product_2.slug),
            json=data
        )
        assert response.status_code == HTTPStatus.CREATED, response.json()
        reviews = (await test_db_session.scalars(select(Review))).all()
        assert len(reviews) == 1
        data.update(
            {
                'id': 1,
                'text': None,
                'user_username': user.username,
                'product_slug': product_2.slug
            }
        )
        check_json_data(response, data)
        check_db_data(response, data, reviews[0])

    @pytest.mark.parametrize('grade', (1, 10))
    async def test_create_review_with_min_rating_1_and_max_10(
        self,
        customer_client: AsyncClient,
        test_db_session: AsyncSession,
        product_2: Product,
        grade: int
    ):
        """Тест для проверки создания отзыва с оценкой от 1 до 10."""
        data = {'grade': grade}
        response = await customer_client.post(
            self.list_url.format(slug=product_2.slug),
            json=data
        )
        count = await test_db_session.scalar(
            select(func.count()).select_from(Review)
        )
        assert count == 1
        assert response.status_code == HTTPStatus.CREATED, response.json()

    @pytest.mark.usefixtures('review_1')
    async def test_cant_create_review_with_already_exists_data(
        self,
        customer_client: AsyncClient,
        test_db_session: AsyncSession,
        product_1: Product
    ):
        """
        Тест для проверки невозможности создания уже существующего отзыва.
        """
        response = await customer_client.post(
            self.list_url.format(slug=product_1.slug),
            json={'grade': 5}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        count = await test_db_session.scalar(
            select(func.count()).select_from(Review)
        )
        assert count == 1

    async def test_supplier_cant_review_own_product(
        self,
        supplier_1_client: AsyncClient,
        test_db_session: AsyncSession,
        product_1: Product
    ):
        """
        Тест для проверки невозможности поставщиком оценивать свой продукт.
        """
        response = await supplier_1_client.post(
            self.list_url.format(slug=product_1.slug), json={'grade': 1}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        count = await test_db_session.scalar(
            select(func.count()).select_from(Review)
        )
        assert count == 0

    @pytest.mark.parametrize(
        'data',
        ({}, {'grade': 'abcd'}, {'grade': 0}, {'grade': 11}),
        ids=('empty_data', 'invalid_text', 'grade_with_0', 'grade_with_10')
    )
    async def test_cant_create_review_with_invalid_data(
        self,
        customer_client: AsyncClient,
        test_db_session: AsyncSession,
        product_1: Product,
        data: dict[str, Any]
    ):
        """
        Тест для проверки невозможности создания отзыва с невалидными данными.
        """
        response = await customer_client.post(
            self.list_url.format(slug=product_1.slug),
            json=data
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        count = await test_db_session.scalar(
            select(func.count()).select_from(Review)
        )
        assert count == 0

    @pytest.mark.parametrize(
        'parametrized_client, review',
        (
            (lf('customer_client'), lf('review_1')),
            (lf('supplier_1_client'), lf('review_2')),
            (lf('admin_client'), lf('review_1'))
        ),
        ids=('customer', 'supplier', 'admin')
    )
    async def test_auth_users_can_patch_review(
        self,
        parametrized_client: AsyncClient,
        review: Review
    ):
        """
        Тест для проверки изменения отзыва авторизованными пользователями.
        """
        data = {'grade': 3, 'text': 'товар не очень'}
        response = await parametrized_client.patch(
            self.detail_url.format(slug=review.product.slug, id=review.id),
            json=data
        )
        assert response.status_code == HTTPStatus.OK
        data.update(
            {
                'id': review.id,
                'product_slug': review.product.slug,
                'user_username': review.user_username
            }
        )
        check_json_data(response, data)
        check_db_data(response, data, review)

    async def test_anon_user_cant_patch_review(
        self,
        client: AsyncClient,
        review_2: Review,
        review_fields: tuple[str, ...]
    ):
        """
        Тест для проверки невозможности
        изменения отзыва анонимным пользователем.
        """
        data = {k: getattr(review_2, k) for k in review_fields}
        response = await client.patch(
            self.detail_url.format(slug=review_2.product.slug, id=review_2.id),
            json={'grade': 8}
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        check_db_data(response, data, review_2)

    @pytest.mark.parametrize(
        'parametrized_client, review',
        (
            (lf('customer_client'), lf('review_2')),
            (lf('supplier_1_client'), lf('review_1')),
        )
    )
    async def test_customer_or_supplier_cant_patch_other_review(
        self,
        parametrized_client: AsyncClient,
        review: Review,
        review_fields: tuple[str, ...]
    ):
        """
        Тест для проверки невозможности изменения
        чужого отзыва покупателем или поставщиком.
        """
        data = {k: getattr(review, k) for k in review_fields}
        response = await parametrized_client.patch(
            self.detail_url.format(slug=review.product.slug, id=review.id),
            json={'grade': 8}
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
        check_db_data(response, data, review)

    @pytest.mark.parametrize(
        'parametrized_client, review',
        (
            (lf('customer_client'), lf('review_1')),
            (lf('supplier_1_client'), lf('review_2')),
            (lf('admin_client'), lf('review_1'))
        ),
        ids=('customer', 'supplier', 'admin')
    )
    async def test_auth_users_can_delete_review(
        self,
        parametrized_client: AsyncClient,
        test_db_session: AsyncSession,
        review: Review
    ):
        """Тест для проверки удаления отзыва авторизованными пользователями."""
        response = await parametrized_client.delete(
            self.detail_url.format(slug=review.product.slug, id=review.id)
        )
        assert response.status_code == HTTPStatus.NO_CONTENT
        count = await test_db_session.scalar(
            select(func.count()).select_from(Review)
        )
        assert count == 0

    async def test_anon_user_cant_delete_review(
        self,
        client: AsyncClient,
        test_db_session: AsyncSession,
        review_2: Review,
    ):
        """
        Тест для проверки невозможности
        удаления отзыва анонимным пользователем.
        """
        response = await client.patch(
            self.detail_url.format(slug=review_2.product.slug, id=review_2.id),
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        count = await test_db_session.scalar(
            select(func.count()).select_from(Review)
        )
        assert count == 1

    @pytest.mark.parametrize(
        'parametrized_client, review',
        (
            (lf('customer_client'), lf('review_2')),
            (lf('supplier_1_client'), lf('review_1'))
        )
    )
    async def test_customer_or_supplier_cant_delete_any_review(
        self,
        parametrized_client: AsyncClient,
        test_db_session: AsyncSession,
        review: Review
    ):
        """
        Тест для проверки невозможности удаления
        чужого отзыва покупателем и поставщиком.
        """
        response = await parametrized_client.patch(
            self.detail_url.format(slug=review.product.slug, id=review.id),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
        count = await test_db_session.scalar(
            select(func.count()).select_from(Review)
        )
        assert count == 1


class TestReviewModel:
    """Класс для тестирования модели отзыва."""

    def test_model_review_fields(self, product_fields: tuple[str, ...]):
        """Тест для проверки наличия ождиаемых полей для модели отзыва."""
        check_db_fields(product_fields, Product)
