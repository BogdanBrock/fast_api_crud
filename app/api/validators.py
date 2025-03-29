"""Модуль для создания валидаторов."""

import jwt

from app.api.exceptions import (BadRequestError,
                                UnauthorizedError,
                                NotFoundError)
from app.models import User
from app.crud.base import ModelType
from app.core.config import settings


async def check_category_exists(category) -> None:
    """Функция для проверки отсутствующей категории."""
    if not category:
        raise NotFoundError('Такой категории не существует.')


async def check_product_exists(product) -> None:
    """Функция для проверки отсутствующего продукта."""
    if not product:
        raise NotFoundError('Такого продукта не существует.')


async def check_review_exists(review) -> None:
    """Функция для проверки отсутствующего отзыва."""
    if not review:
        raise NotFoundError('Такого отзыва не существует.')


async def check_object_duplicate(obj: ModelType) -> None:
    """Функция для проверки уже существующего объекта."""
    if obj:
        raise BadRequestError('Нельзя создать дважды.')


async def user_cant_create_review_own_product(user, obj_user) -> None:
    if user == obj_user:
        raise BadRequestError('Нельзя оставлять отзыв на свой родукт')


async def validate_credentials(user: User, is_password_hashed: str) -> None:
    if not user and not is_password_hashed:
        raise UnauthorizedError('Не правильные учетные данные')


async def validate_and_decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token,
                             settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError('Срок действия токена истек')
    except jwt.PyJWTError:
        raise UnauthorizedError('Недействительный токен')
    return payload
