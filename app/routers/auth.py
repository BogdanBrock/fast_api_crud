from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models.users import User
from app.schemas import UserSchema
from app.backend.db_depends import get_db
from app.models.users import RoleEnum

router = APIRouter(prefix='/auth', tags=['auth'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token/')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

SECRET_KEY = '6d97dfbc72b42506d9e109b58238f9accd67c6ccf25477dbcf76ba2a17d8d573'
ALGORITHM = 'HS256'


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(
    session: Annotated[AsyncSession, Depends(get_db)],
    user_schema: UserSchema
) -> UserSchema:
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
    user = await authenticate_user(
        session,
        form_data.username,
        form_data.password
    )
    token = await create_access_token(
        user.id,
        user.username,
        user.role,
        expires_delta=timedelta(minutes=20)
    )
    return {
        'access_token': token,
        'token_type': 'bearer'
    }


async def authenticate_user(
    session: Annotated[AsyncSession, Depends(get_db)],
    username: str,
    password: str
):
    user = await session.scalar(
        select(User).
        where(User.username == username)
    )
    is_hashed_password = bcrypt_context.verify(password, user.password)
    if not user or not is_hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не правильные учетные данные',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return user


async def create_access_token(
    id: int,
    username: str,
    role: RoleEnum,
    expires_delta: timedelta
):
    payload = {
        'id': id,
        'sub': username,
        'role': role,
        'exp': int(
            (datetime.now(timezone.utc) + expires_delta).timestamp()
        )
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
    return {
        'id': payload.get('id'),
        'username': payload.get('sub'),
        'role': payload.get('role')
    }


@router.get('/read_current_user/')
async def read_current_user(user: dict = Depends(get_current_user)):
    return {'User': user}
