from typing import Annotated

from fastapi import Depends, HTTPException, status
from pydantic import (
    BaseModel, EmailStr, Field, model_validator, field_validator
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.core.enums import RoleEnum
from app.core.dependencies import get_db


class UserSchema(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.IS_CUSTOMER

    # @model_validator(mode='after')
    # async def validate(self):
    #     user = await self.get_user(self.username, self.password)
    #     if user and user.username == self.username:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail='Уже есть такое имя пользователя'
    #         )
    #     if user and user.email == self.email:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail='Уже есть такая почта'
    #         )
    #     if self.role not in RoleEnum:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail=('Нужно выбрать между: '
    #                     'администратор, поставщик, покупатель')
    #         )
    #     return self

    # @staticmethod
    # async def get_user(username, password):
    #     session = get_db()
    #     user = await session.scalar(
    #         select(User).
    #         where((User.username == username) |
    #               (User.email == password))
    #     )
    #     return user


class ProductSchema(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category_id: int


class CategorySchema(BaseModel):
    name: str
    parent_id: int | None = None


class ReviewSchema(BaseModel):
    text: str | None = None
    grade: int = Field(ge=0, le=10)
