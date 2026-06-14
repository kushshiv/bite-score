from fastapi import APIRouter

from app.api.routes import auth, billing, businesses, dashboard, reviews, uploads

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(businesses.router)
api_router.include_router(reviews.router)
api_router.include_router(uploads.router)
api_router.include_router(dashboard.router)
api_router.include_router(billing.router)
