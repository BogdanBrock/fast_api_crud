"""Модуль для создания схем."""

from pydantic import BaseModel, HttpUrl, Field, computed_field
from slugify import slugify

from app.core.constants import (PRODUCT_NAME_MAX_LENGTH,
                                PRODUCT_IMAGE_URL_MAX_LENGTH)


class ProductSchema(BaseModel):
    """Схема ProductSchema для валидации данных."""

    name: str = Field(max_length=PRODUCT_NAME_MAX_LENGTH)
    description: str | None = None
    image_url: HttpUrl | None = Field(max_length=PRODUCT_IMAGE_URL_MAX_LENGTH,
                                      default=None)
    price: float = Field(ge=1)
    stock: int = Field(ge=0)
    category_id: int = Field(ge=1)

    @computed_field()
    def slug(self) -> str:
        """Функция для вычисления поля slug у продукта."""
        return slugify(self.name)
