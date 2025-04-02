"""Модуль для создания основного маршрута."""

from fastapi import APIRouter

from app.api.endpoints import (auth_router, category_router, product_router,
                               review_router, user_router)

main_router = APIRouter(prefix='/api/v1')

main_router.include_router(
    category_router, prefix='/categories', tags=['Category']
)
main_router.include_router(
    product_router, prefix='/products', tags=['Product']
)
main_router.include_router(
    review_router, tags=['Review']
)
main_router.include_router(auth_router, prefix='/auth', tags=['Auth'])
main_router.include_router(user_router, prefix='/users', tags=['Users'])
