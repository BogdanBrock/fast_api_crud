"""Модуль создания фикстур для отзывов."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession


from app.models import Review, Product, User
from ..utils import create_db_obj

CREATE_URL = '/api/v1/products/{slug}/reviews/'
DETAIL_URL = f'{CREATE_URL}' + '{id}/'


@pytest_asyncio.fixture
async def review_1(
    test_db_session: AsyncSession,
    product_1: Product,
    customer: User
) -> Review:
    review = Review(
        grade=1,
        text='плохой товар',
        user_username=customer.username,
        product_slug=product_1.slug
    )
    return await create_db_obj(test_db_session, review)


@pytest_asyncio.fixture
async def review_2(
    test_db_session: AsyncSession,
    product_2: Product,
    supplier_1: User
) -> Review:
    review = Review(
        grade=5,
        text='неплохой товар',
        user_username=supplier_1.username,
        product_slug=product_2.slug
    )
    return await create_db_obj(test_db_session, review)


@pytest_asyncio.fixture
async def review_3(
    test_db_session: AsyncSession,
    product_1: Product,
    admin: User
) -> Review:
    review = Review(
        grade=10,
        text='лучший товар',
        user_username=admin.username,
        product_slug=product_1.slug
    )
    return await create_db_obj(test_db_session, review)


@pytest.fixture
def review_fields() -> tuple[str, ...]:
    return ('id', 'grade', 'text', 'product_slug', 'user_username')
