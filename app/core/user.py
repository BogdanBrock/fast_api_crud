"""Модуль для реализации бизнес-логики пользователя."""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (validate_and_decode_token,
                                validate_credentials)
from app.core.config import settings
from app.core.db import db_session
from app.crud import user_crud
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token/')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password: str) -> str:
    """Функция для получения закодированного пароля."""
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    """Функция для проверки закодированного пароля."""
    return bcrypt_context.verify(plain_password, hashed_password)


async def authenticate_user(
    username: str,
    password: str,
    session: AsyncSession = Depends(db_session)
) -> User:
    """Функция для аутентификации пользователя."""
    user = await user_crud.get_user_by_username(username, session)
    is_password_hashed = verify_password(password, user.password)
    await validate_credentials(user, is_password_hashed)
    return user


async def create_access_token(
    username: str,
    expiration_time: int
) -> str:
    """Функция для создания токена."""
    exp = datetime.now(timezone.utc) + timedelta(minutes=expiration_time)
    payload = {'sub': username,
               'exp': int(exp.timestamp())}
    return jwt.encode(payload,
                      settings.SECRET_KEY,
                      algorithm=settings.ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db_session)
) -> User | None:
    """Функция для получения текущего пользователя."""
    payload = await validate_and_decode_token(token)
    return await user_crud.get_user_by_username(payload.get('sub'), session)
