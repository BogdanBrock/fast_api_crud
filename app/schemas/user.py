"""Модуль для создания схем."""

from pydantic import BaseModel, EmailStr, Field

from app.core.constants import (USER_FIRST_NAME_MAX_LENGTH,
                                USER_LAST_NAME_MAX_LENGTH,
                                USER_PASSWORD_MAX_LENGTH,
                                USER_EMAIL_MAX_LENGTH,
                                USER_USERNAME_PATTERN)
from app.core.enums import RoleEnum


class UserSchema(BaseModel):
    """Схема UserSchema для валидации данных."""

    first_name: str = Field(max_length=USER_FIRST_NAME_MAX_LENGTH)
    last_name: str = Field(max_length=USER_LAST_NAME_MAX_LENGTH)
    username: str = Field(pattern=USER_USERNAME_PATTERN)
    email: EmailStr = Field(max_length=USER_EMAIL_MAX_LENGTH)
    password: str = Field(max_length=USER_PASSWORD_MAX_LENGTH)
    role: RoleEnum = RoleEnum.IS_CUSTOMER
