"""Модуль для создания маршрутов."""

from datetime import timedelta

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.crud import user_crud
from app.core.constants import EXPIRATION_TIME
from app.core.db import db_session
from app.core.user import (authenticate_user,
                           create_access_token,
                           get_current_user,
                           get_hashed_password)
from app.api.validators import check_user_already_exists
from app.models import User
from app.schemas.user import UserCreateSchema, UserUpdateSchema, UserReadSchema

auth_router = APIRouter()
user_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token/')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@auth_router.post(
    '/registration/',
    status_code=status.HTTP_201_CREATED,
    response_model=UserReadSchema
)
async def create_user(
    user_schema: UserCreateSchema,
    session: AsyncSession = Depends(db_session)
):
    """Маршрут для регистрации пользователя."""
    await check_user_already_exists(
        user_schema.username, user_schema.email, session
    )
    user_schema = await get_hashed_password(user_schema)
    return await user_crud.create(user_schema, session)


@auth_router.post(
    '/token/',
    status_code=status.HTTP_201_CREATED
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(db_session)
) -> dict:
    """Маршрут для авторизации пользвателя."""
    user = await authenticate_user(
        form_data.username, form_data.password, session
    )
    token = await create_access_token(
        user.username,
        expires_delta=timedelta(minutes=EXPIRATION_TIME)
    )
    return {'access_token': token,
            'token_type': 'bearer'}


@user_router.get('/me/', response_model=UserReadSchema)
async def get_user(user: User = Depends(get_current_user)):
    """Маршрут для просмотра профиля."""
    return user


@user_router.patch(
    '/me/',
    response_model=UserReadSchema
)
async def update_user(
    user_schema: UserUpdateSchema,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_session)
):
    """Маршрут для изменения профиля."""
    await check_user_already_exists(
        user_schema.username,
        user_schema.email,
        session
    )
    return await user_crud.update(user, user_schema, session)


@user_router.delete(
    '/me/',
    response_model=None
)
async def delete_user(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_session)
):
    """Маршрут для удаления профиля."""
    await user_crud.delete(user, session)
