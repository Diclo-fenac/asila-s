from fastapi import APIRouter

from app.api.routes import analytics, auth, broadcasts, notices, webhook

api_router = APIRouter()
api_router.include_router(webhook.router, tags=["webhook"])
api_router.include_router(auth.router, prefix="/api", tags=["auth"])
api_router.include_router(notices.router, prefix="/api", tags=["notices"])
api_router.include_router(broadcasts.router, prefix="/api", tags=["broadcasts"])
api_router.include_router(analytics.router, prefix="/api", tags=["analytics"])
