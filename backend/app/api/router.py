"""
API Router - Main router configuration
"""
from fastapi import APIRouter
from app.api.endpoints import tank

api_router = APIRouter()

api_router.include_router(
    tank.router,
    prefix="/tank",
    tags=["Tank Configuration"]
)
