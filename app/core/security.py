"""Модуль для реализации авторизации и токенов пользователя."""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError, ValidationError
from app.core.config import settings
from app.core.db import db_session
from app.crud import user_crud
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login/')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def authenticate_user(
    username: str,
    password: str,
    session: AsyncSession = Depends(db_session)
) -> User:
    """Функция для аутентификации пользователя."""
    user = await user_crud.get_user_by_username(username, session)
    if user:
        is_password_hashed = bcrypt_context.verify(password, user.password)
    if not (user and is_password_hashed):
        raise ValidationError('Не правильные учетные данные')
    return user


def create_access_token(
    username: str,
    expiration_time: int
) -> str:
    """Функция для создания токена."""
    exp = datetime.now(timezone.utc) + timedelta(minutes=expiration_time)
    payload = {
        'sub': username,
        'exp': int(exp.timestamp())
    }
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


async def validate_and_decode_token(token: str) -> dict | None:
    """Функция для валидации и декодирования токена."""
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


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db_session)
) -> User | None:
    """Функция для получения текущего пользователя."""
    payload = await validate_and_decode_token(token)
    return await user_crud.get_user_by_username(payload.get('sub'), session)
