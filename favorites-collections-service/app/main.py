"""
Favorites & Collections Service - Main Application Entry Point

A microservice for managing user favorites and collections
in the Smart Hospitality & Retail platform.

This service allows users to:
- Save and unsave places (favorites)
- Create, update, and delete collections
- Add and remove places inside collections
- List user favorites and collections
- Access public (shareable) collections via a public identifier

Design principles:
- Clear separation between favorites and collections
- Proper ownership checks (users can only modify their own data)
- Idempotent favorite operations
- Soft deletes where appropriate
- Simple, frontend-friendly error handling
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db, close_db
from app.exceptions import register_exception_handlers
from app.api.v1 import router as v1_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    
    - On startup: Initialize database tables
    - On shutdown: Close database connections
    """
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create the FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## Favorites & Collections Service
    
    A microservice for managing user favorites and collections in the 
    Smart Hospitality & Retail platform.
    
    ### Features
    
    **Favorites:**
    - Add/remove places to favorites (idempotent)
    - List all favorites with pagination
    - Check favorite status for single or multiple places
    - Toggle favorite status
    
    **Collections:**
    - Create collections with custom names and descriptions
    - Update collection metadata and visibility
    - Add/remove places to collections
    - Reorder items within collections (drag-and-drop support)
    - Share collections via public links
    - Regenerate public IDs to revoke share access
    
    ### Authentication
    
    All endpoints except public collection access require JWT authentication.
    Pass the token in the Authorization header: `Bearer <token>`
    
    ### Note on Place Data
    
    This service only stores place IDs as opaque strings. It does not store
    place details, prices, reviews, or booking information. The frontend
    should fetch these details from the appropriate services.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Register custom exception handlers for consistent error responses
register_exception_handlers(app)

# Configure CORS
# In production, restrict origins to your frontend domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(v1_router, prefix=settings.API_V1_PREFIX)


# =============================================================================
# Root Endpoints
# =============================================================================

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to docs."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.
    
    Returns basic service status. For more detailed health checks
    (database connectivity, etc.), implement a /health/detailed endpoint.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check for Kubernetes or similar orchestrators.
    
    Checks if the service is ready to accept traffic.
    """
    # TODO: Add database connectivity check if needed
    return {"status": "ready"}


# =============================================================================
# Development Server
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run with: python -m app.main
    # Or: uvicorn app.main:app --reload --port 8007
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )


