"""Файл для инициализации пакета."""

from .category import router as category_router
from .product import router as product_router
from .review import router as review_router
from .user import auth_router, user_router
