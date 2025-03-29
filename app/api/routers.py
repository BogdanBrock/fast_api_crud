"""Модуль для создания основного маршрута."""

from fastapi import APIRouter

from app.api.endpoints import (category_router,
                               product_router,
                               review_router,
                               auth_router,
                               user_router)

main_router = APIRouter(prefix='/api/v1')

main_router.include_router(
    category_router, prefix='/category', tags=['Category']
)
main_router.include_router(
    product_router, prefix='/product', tags=['Product']
)
main_router.include_router(
    review_router, tags=['Review']
)
main_router.include_router(auth_router, prefix='/auth', tags=['Auth'])
main_router.include_router(user_router, prefix='/users', tags=['Users'])
