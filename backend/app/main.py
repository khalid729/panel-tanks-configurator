"""
GRP Panel Tank Configuration API - Main Application
Al Muhaideb National Tanks
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## GRP Panel Tank Configuration System API

This API provides endpoints for configuring GRP (Glass Reinforced Plastic) panel tanks.

### Features:
- **Tank Calculation**: Calculate complete BOM, costs, and weights
- **Capacity Calculation**: Quick capacity and surface area calculation
- **Input Options**: Get all available configuration options
- **Price Lookup**: Search part prices and weights

### Main Endpoints:
- `POST /api/v1/tank/calculate` - Full tank configuration calculation
- `POST /api/v1/tank/capacity` - Quick capacity calculation
- `GET /api/v1/tank/options` - Get available input options
- `GET /api/v1/tank/prices` - List all parts with prices
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
