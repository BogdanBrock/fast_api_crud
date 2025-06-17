"""Модуль создания тестов для отзывов."""

from http import HTTPStatus

import pytest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pytest_lazy_fixtures import lf
from httpx import AsyncClient

from app.models import Review, Product, User
from .fixtures.fixture_reviews import CREATE_URL, DETAIL_URL
from .utils import check_json_data, check_db_data, check_db_fields


async def test_anon_user_can_get_reviews(client: AsyncClient):
    response = await client.get('api/v1/reviews/')
    assert response.status_code == HTTPStatus.OK, response.json()


async def test_anon_user_can_get_review(client: AsyncClient, review_1: Review):
    response = await client.get(DETAIL_URL.format(
        slug=review_1.product.slug,
        id=review_1.id
    ))
    assert response.status_code == HTTPStatus.OK, response.json()


async def test_review_not_found(client: AsyncClient):
    """Тест для проверки отсутствия отзыва."""
    response = await client.get(DETAIL_URL.format(slug='product', id=1))
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'parametrized_client, user, data',
    (
        (lf('customer_client'), lf('customer'), {'grade': 1, 'text': None}),
        (lf('supplier_1_client'), lf('supplier_1'), {'grade': 5}),
        (lf('admin_client'), lf('admin'), {'grade': 10})
    )
)
async def test_users_can_create_review(
    parametrized_client: AsyncClient,
    test_db_session: AsyncSession,
    user: User,
    product_2: Product,
    data: dict,
):
    response = await parametrized_client.post(
        CREATE_URL.format(slug=product_2.slug),
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
    review = reviews[0]
    check_db_data(response, data, review)


@pytest.mark.usefixtures('review_1')
async def test_cant_create_review_one_more(
    customer_client: AsyncClient,
    test_db_session: AsyncSession,
    product_1: Product
):
    response = await customer_client.post(
        CREATE_URL.format(slug=product_1.slug),
        json={'grade': 5}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    count = await test_db_session.scalar(
        select(func.count()).select_from(Review)
    )
    assert count == 1


async def test_supplier_cant_review_own_product(
    supplier_1_client: AsyncClient,
    test_db_session: AsyncSession,
    product_1: Product
):
    response = await supplier_1_client.post(
        CREATE_URL.format(slug=product_1.slug), json={'grade': 1}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    count = await test_db_session.scalar(
        select(func.count()).select_from(Review)
    )
    assert count == 0


@pytest.mark.parametrize(
    'data',
    ({}, {'grade': 'abcd'}, {'grade': 0}, {'grade': 11})
)
async def test_cant_create_review_with_invalid_data(
    customer_client: AsyncClient,
    test_db_session: AsyncSession,
    product_1: Product,
    data: dict
):
    response = await customer_client.post(
        CREATE_URL.format(slug=product_1.slug),
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
        (lf('admin_client'), lf('review_1')),
        (lf('admin_client'), lf('review_2')),
        (lf('admin_client'), lf('review_3'))
    )
)
async def test_users_can_update_review(
    parametrized_client: AsyncClient,
    review: Review
):
    data = {'grade': 3, 'text': 'такое себе'}
    response = await parametrized_client.patch(
        DETAIL_URL.format(slug=review.product.slug, id=review.id), json=data
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


@pytest.mark.parametrize(
    'parametrized_client, review, expected_status',
    (
        (lf('client'), lf('review_2'), HTTPStatus.UNAUTHORIZED),
        (lf('customer_client'), lf('review_2'), HTTPStatus.FORBIDDEN),
        (lf('customer_client'), lf('review_3'), HTTPStatus.FORBIDDEN),
        (lf('supplier_1_client'), lf('review_1'), HTTPStatus.FORBIDDEN),
        (lf('supplier_1_client'), lf('review_3'), HTTPStatus.FORBIDDEN)
    )
)
async def test_users_cant_update_any_review(
    parametrized_client: AsyncClient,
    review: Review,
    expected_status: int,
    review_fields: tuple[str, ...]
):
    data = {k: getattr(review, k) for k in review_fields}
    response = await parametrized_client.patch(
        DETAIL_URL.format(slug=review.product.slug, id=review.id),
        json={'grade': 8}
    )
    assert response.status_code == expected_status
    check_db_data(response, data, review)


@pytest.mark.parametrize(
    'parametrized_client, review',
    (
        (lf('customer_client'), lf('review_1')),
        (lf('supplier_1_client'), lf('review_2')),
        (lf('admin_client'), lf('review_1')),
        (lf('admin_client'), lf('review_2')),
        (lf('admin_client'), lf('review_3'))
    )
)
async def test_users_can_delete_review(
    parametrized_client: AsyncClient,
    test_db_session: AsyncSession,
    review: Review
):
    response = await parametrized_client.delete(
        DETAIL_URL.format(slug=review.product.slug, id=review.id)
    )
    assert response.status_code == HTTPStatus.NO_CONTENT
    count = await test_db_session.scalar(
        select(func.count()).select_from(Review)
    )
    assert count == 0


@pytest.mark.parametrize(
    'parametrized_client, review, expected_status',
    (
        (lf('client'), lf('review_2'), HTTPStatus.UNAUTHORIZED),
        (lf('customer_client'), lf('review_2'), HTTPStatus.FORBIDDEN),
        (lf('customer_client'), lf('review_3'), HTTPStatus.FORBIDDEN),
        (lf('supplier_1_client'), lf('review_1'), HTTPStatus.FORBIDDEN),
        (lf('supplier_1_client'), lf('review_3'), HTTPStatus.FORBIDDEN)
    )
)
async def test_users_cant_delete_any_review(
    parametrized_client: AsyncClient,
    test_db_session: AsyncSession,
    review: Review,
    expected_status: int,
):
    response = await parametrized_client.patch(
        DETAIL_URL.format(slug=review.product.slug, id=review.id),
    )
    assert response.status_code == expected_status
    count = await test_db_session.scalar(
        select(func.count()).select_from(Review)
    )
    assert count == 1
