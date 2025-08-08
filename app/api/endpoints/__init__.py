"""Файл для инициализации пакета."""

from .categories import router as category_router
from .products import router as product_router
from .reviews import router as review_router
from .users import auth_router, user_router
