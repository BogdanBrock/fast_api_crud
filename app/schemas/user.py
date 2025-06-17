"""Модуль для создания схем модели User."""

from pydantic import BaseModel, EmailStr, Field

from app.core.constants import (USER_EMAIL_MAX_LENGTH,
                                USER_FIRST_NAME_MAX_LENGTH,
                                USER_LAST_NAME_MAX_LENGTH,
                                USER_PASSWORD_MAX_LENGTH, USER_USERNAME_REGEXP)
from app.models import RoleEnum


class UserUpdateSchema(BaseModel):
    """Схема UserUpdateSchema для валидации и обновления данных."""

    first_name: str = Field(max_length=USER_FIRST_NAME_MAX_LENGTH,
                            default=None)
    last_name: str = Field(max_length=USER_LAST_NAME_MAX_LENGTH, default=None)
    username: str = Field(pattern=USER_USERNAME_REGEXP, default=None)
    email: EmailStr = Field(max_length=USER_EMAIL_MAX_LENGTH, default=None)
    password: str = Field(max_length=USER_PASSWORD_MAX_LENGTH, default=None)


class UserCreateSchema(BaseModel):
    """Схема UserCreateSchema для валидации и создания данных."""

    first_name: str = Field(max_length=USER_FIRST_NAME_MAX_LENGTH)
    last_name: str = Field(max_length=USER_LAST_NAME_MAX_LENGTH)
    username: str = Field(pattern=USER_USERNAME_REGEXP)
    email: EmailStr = Field(max_length=USER_EMAIL_MAX_LENGTH)
    password: str = Field(max_length=USER_PASSWORD_MAX_LENGTH)
    role: RoleEnum = RoleEnum.CUSTOMER


class UserReadSchema(BaseModel):
    """Схема UserReadSchema для чтения данных."""

    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    role: RoleEnum
