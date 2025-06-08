"""Модуль для создания маршрутов."""

from datetime import timedelta

from fastapi import APIRouter, Depends, status
from fastapi.security import (OAuth2PasswordBearer,
                              OAuth2PasswordRequestForm)
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_user_already_exists
from app.core.config import settings
from app.core.db import db_session
from app.core.user import (authenticate_user, create_access_token,
                           get_current_user, get_hashed_password)
from app.crud import user_crud
from app.models import User
from app.schemas.user import (UserCreateSchema,
                              UserReadSchema,
                              UserUpdateSchema)

auth_router = APIRouter()
user_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token/')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@auth_router.post(
    '/token/',
    status_code=status.HTTP_201_CREATED
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(db_session)
) -> dict[str, str]:
    """Маршрут для авторизации пользователя."""
    user = await authenticate_user(
        form_data.username,
        form_data.password,
        session
    )
    token = await create_access_token(
        user.username,
        expiration_time=settings.TOKEN_EXPIRE
    )
    return {'access_token': token,
            'token_type': 'bearer'}


@user_router.get('/me/', response_model=UserReadSchema)
async def get_user(user: User = Depends(get_current_user)):
    """Маршрут для просмотра профиля."""
    return user


@user_router.post(
    '/registration/',
    status_code=status.HTTP_201_CREATED,
    response_model=UserReadSchema
)
async def create_user(
    schema: UserCreateSchema,
    session: AsyncSession = Depends(db_session)
):
    """
    Маршрут для регистрации пользователя.

    Доступны такие роли как: "покупатель", "поставщик", "администратор".
    """
    await check_user_already_exists(
        schema.username,
        schema.email,
        session
    )
    hashed_password = get_hashed_password(schema.password)
    schema = schema.model_copy(update={'password': hashed_password})
    return await user_crud.create(schema, session)


@user_router.patch(
    '/me/',
    response_model=UserReadSchema
)
async def update_user(
    schema: UserUpdateSchema,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_session)
):
    """Маршрут для изменения профиля."""
    await check_user_already_exists(schema.username, schema.email, session)
    return await user_crud.update(user, schema, session)


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
