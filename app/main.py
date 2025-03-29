"""Модуль для создания приложения. Основная точка входа."""

import uvicorn
from fastapi import FastAPI

from app.api.routers import main_router

app = FastAPI()

app.include_router(main_router)


if __name__ == '__main__':
    uvicorn.run(
        'app.main:app',
        host='127.0.0.1',
        port=8000,
        reload=True
    )
