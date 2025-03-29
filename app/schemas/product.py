"""Модуль для создания схем."""

from fastapi import HTTPException, status
from pydantic import HttpUrl, Field, model_validator, field_validator

from .base import AbstractBaseModel
from app.core.constants import (PRODUCT_NAME_MAX_LENGTH,
                                PRODUCT_IMAGE_URL_MAX_LENGTH)


class ProductSchema(AbstractBaseModel):
    """Схема ProductSchema для валидации данных."""

    name: str = Field(max_length=PRODUCT_NAME_MAX_LENGTH)
    description: str | None = None
    image_url: HttpUrl | None = Field(max_length=PRODUCT_IMAGE_URL_MAX_LENGTH,
                                      default=None)
    price: float
    stock: int
    category_id: int

    @field_validator('image_url', mode='after')
    @classmethod
    def validate_image_url(cls, value) -> str:
        return str(value)

    @model_validator(mode='after')
    def validate(self):
        if self.price <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Цена продукта не может '
                                       'быть ниже единицы.')
        if self.stock < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Наличие продукта не может '
                                       'быть отрицательным.')
        return self
