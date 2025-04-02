"""Модуль для создания валидаторов."""

import jwt

from app.api.exceptions import (BadRequestError,
                                NotFoundError,
                                UnauthorizedError)
from app.core.config import settings
from app.core.db import AsyncSession
from app.crud import category_crud, product_crud, review_crud, user_crud
from app.crud.base import ModelType
from app.models import Category, Product, Review, User


async def get_category_or_not_found(
    category_slug: str,
    session: AsyncSession,
) -> Category | None:
    """Функция для проверки существования категории и получения категории."""
    category = await category_crud.get_object_by_slug(category_slug, session)
    if not category:
        raise NotFoundError('Такой категории не существует.')
    return category


async def get_product_or_not_found(
    product_slug: str,
    session: AsyncSession
) -> Product | None:
    """Функция для проверки существования продукта и получения продукта."""
    product = await product_crud.get_object_by_slug(product_slug, session)
    if not product:
        raise NotFoundError('Такого продукта не существует.')
    return product


async def get_review_or_not_found(
    review_id: int,
    session: AsyncSession
) -> Review | None:
    """Функция для проверки существования отзыва и получения отзыва."""
    review = await review_crud.get(review_id, session)
    if not review:
        raise NotFoundError('Такого отзыва не существует.')
    return review


async def check_category_already_exists(
    category_slug: str,
    session: AsyncSession
) -> Category | None:
    """Функция для проверки уже существующей категории."""
    category = await category_crud.get_object_by_slug(category_slug, session)
    if category:
        raise BadRequestError('Нельзя создать две одинаковые категории.')


async def check_product_already_exists(
    product_slug: str,
    session: AsyncSession
) -> Product | None:
    """Функция для проверки уже существующего продукта."""
    product = await product_crud.get_object_by_slug(product_slug, session)
    if product:
        raise BadRequestError('Нельзя создать два одинаковых продукта.')


async def check_review_already_exists(
    product_slug: str,
    username: str,
    session: AsyncSession
) -> Review | None:
    """Функция для проверки уже существующего отзыва."""
    review = await review_crud.get_review_by_product_slug_and_username(
        product_slug,
        username,
        session
    )
    if review:
        raise BadRequestError('Вы уже оставили отзыв на этот продукт.')


async def check_cant_review_own_product(
    current_username: str,
    review_username: ModelType
) -> None:
    if current_username == review_username:
        raise BadRequestError('Нельзя оставлять отзыв на свой продукт')


async def check_user_already_exists(
    username: str,
    email: str,
    session: AsyncSession
) -> None:
    """Функция для проверки уже существующего пользователя категории."""
    data = await user_crud.get_username_and_email(username, email, session)
    if data and username == data.get('username'):
        raise BadRequestError('Такое имя пользователя уже существует.')
    if data and email == data.get('email'):
        raise BadRequestError('Такая почта уже существует.')


async def validate_credentials(user: User, is_password_hashed: str) -> None:
    if not user and not is_password_hashed:
        raise UnauthorizedError('Не правильные учетные данные')


async def validate_and_decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError('Срок действия токена истек')
    except jwt.PyJWTError:
        raise UnauthorizedError('Недействительный токен')
    return payload
