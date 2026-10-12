from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.scan import router as scan_router
from app.api.analyze import router as analyze_router
from app.api.scans import router as scans_router
from app.api.dashboard import router as dashboard_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(scan_router)
api_router.include_router(analyze_router)
api_router.include_router(scans_router)
api_router.include_router(dashboard_router)

__all__ = ["api_router"]

