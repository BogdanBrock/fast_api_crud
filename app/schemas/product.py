"""Модуль для создания схем."""

from pydantic import HttpUrl, Field, field_validator

from app.schemas import AbstractBaseModel
from app.core.constants import (PRODUCT_NAME_MAX_LENGTH,
                                PRODUCT_IMAGE_URL_MAX_LENGTH)


class ProductSchema(AbstractBaseModel):
    """Схема ProductSchema для валидации данных."""

    name: str = Field(max_length=PRODUCT_NAME_MAX_LENGTH)
    description: str | None = None
    image_url: HttpUrl | None = Field(max_length=PRODUCT_IMAGE_URL_MAX_LENGTH,
                                      default=None)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    category_id: int

    @field_validator('image_url', mode='after')
    @classmethod
    def validate_image_url(cls, value) -> str:
        return str(value)
