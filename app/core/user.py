"""Модуль для реализации бизнес-логики пользователя."""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.api.validators import validate_credentials, validate_and_decode_token
from app.crud import user_crud
from app.schemas import UserSchema
from app.models import User
from app.core.db import db_session
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token/')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def get_hashed_password(user_schema: UserSchema) -> UserSchema:
    """Функция для получения закодированного пароля."""
    hashed_password = bcrypt_context.hash(user_schema.password)
    return user_schema.model_copy(update={'password': hashed_password})


async def authenticate_user(
    username: str,
    password: str,
    session: AsyncSession = Depends(db_session)
) -> User:
    """Функция для аутентификации пользователя."""
    user = await get_user(username, session)
    is_password_hashed = verify_password(password, user.password)
    await validate_credentials(user, is_password_hashed)
    return user


async def get_user(username: str, session: AsyncSession) -> User:
    """Функция для получения пользователя."""
    return await user_crud.get_user_by_username(username, session)


async def verify_password(password: str, hashed_password: str) -> bool:
    """Функция для проверки закодированного пароля."""
    return bcrypt_context.verify(password, hashed_password)


async def create_access_token(
    username: str,
    expires_delta: timedelta
) -> str:
    """Функция для создания токена."""
    expiration_time = datetime.now(timezone.utc) + expires_delta
    payload = {'sub': username,
               'exp': int(expiration_time.timestamp())}
    return jwt.encode(payload,
                      settings.SECRET_KEY,
                      algorithm=settings.ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db_session)
) -> User | None:
    """Функция для получения текущего пользователя."""
    payload = await validate_and_decode_token(token)
    return await get_user(payload.get('sub'), session)
