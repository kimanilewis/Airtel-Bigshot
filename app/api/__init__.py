"""
Package initialization for app API endpoints.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api")

from app.api.validate import router as validate_router
from app.api.process import router as process_router

# Include routers
router.include_router(validate_router, prefix="/validate", tags=["validate"])
router.include_router(process_router, prefix="/process", tags=["process"])

__all__ = [
    'router',
]
