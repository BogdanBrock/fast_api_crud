import uvicorn
from fastapi import FastAPI, APIRouter

from app.api.endpoints import category, product, user
from app.api.endpoints import review

api_router = APIRouter(prefix='/api/v1')
api_router.include_router(category.router)
api_router.include_router(product.router)
api_router.include_router(user.router)
api_router.include_router(review.router)

app = FastAPI()
app.include_router(api_router)

if __name__ == '__main__':
    uvicorn.run(
        'app.main:app',
        host='127.0.0.1',
        port=8000,
        reload=True
    )
