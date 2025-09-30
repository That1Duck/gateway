from fastapi import APIRouter
from ...core.config import settings
from ...schemas.common import HealthResponse

"""
Small router for system endpoints
- api/v1/system/health -> checks if connection is relevant
- api/v1/system/version -> shows version of app
"""

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(ok=True, name=settings.APP_NAME, version=settings.APP_VERSION)

@router.get("/version")
def version():
    return {"version": settings.APP_VERSION}