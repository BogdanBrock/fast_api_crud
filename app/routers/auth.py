"""Модуль для создания маршрутов."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.user import UserSchema
from app.core.db import get_db
from app.core.config import settings

router = APIRouter(prefix='/auth', tags=['auth'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token/')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(
    session: Annotated[AsyncSession, Depends(get_db)],
    user_schema: UserSchema
) -> UserSchema:
    """Маршрут для регистрации пользователя."""
    user = user_schema.model_dump()
    user['password'] = bcrypt_context.hash(user.get('password'))
    await session.execute(
        insert(User).
        values(**user)
    )
    await session.commit()
    return user


@router.post('/token/', status_code=status.HTTP_201_CREATED)
async def login(
    session: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """Маршрут для авторизации пользователя."""
    user = await authenticate_user(
        session,
        form_data.username,
        form_data.password
    )
    token = await create_access_token(
        user.username,
        expires_delta=timedelta(minutes=20)
    )
    return {
        'access_token': token,
        'token_type': 'bearer'
    }


async def get_user(session, username):
    """Функция для получения пользователя."""
    user = await session.scalar(
        select(User).
        where(User.username == username)
    )
    return user


async def authenticate_user(
    session: Annotated[AsyncSession, Depends(get_db)],
    username: str,
    password: str
):
    """Функция для аутентификации пользователя."""
    user = await get_user(session, username)
    is_hashed_password = bcrypt_context.verify(password, user.password)
    if not user or not is_hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не правильные учетные данные',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return user


async def create_access_token(
    username: str,
    expires_delta: timedelta
):
    """Функция для создания токена."""
    payload = {
        'sub': username,
        'exp': int(
            (datetime.now(timezone.utc) + expires_delta).timestamp()
        )
    }
    return jwt.encode(payload,
                      settings.SECRET_KEY,
                      algorithm=settings.ALGORITHM)


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)]
):
    """Функция для получения текущего пользователя."""
    try:
        payload: dict = jwt.decode(token,
                                   settings.SECRET_KEY,
                                   algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Срок действия токена истек'
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Недействительный токен'
        )
    user = await get_user(session, payload.get('sub'))
    return user


@router.get('/me/')
async def me(user: User = Depends(get_current_user)):
    """Маршрут для просмотра профиля."""
    return user
