"""Модуль для создания схем."""

from fastapi import HTTPException, status
from pydantic import BaseModel, HttpUrl, Field, model_validator

from .mixins import SlugMixin
from app.core.constants import (PRODUCT_NAME_MAX_LENGTH,
                                PRODUCT_IMAGE_URL_MAX_LENGTH)


class ProductSchema(BaseModel, SlugMixin):
    """Схема ProductSchema для валидации данных."""

    name: str = Field(max_length=PRODUCT_NAME_MAX_LENGTH)
    description: str | None = None
    image_url: HttpUrl | None = Field(max_length=PRODUCT_IMAGE_URL_MAX_LENGTH,
                                      default=None)
    price: float
    stock: int
    category_id: int

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
