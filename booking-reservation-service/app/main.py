"""
Main FastAPI application for the Booking & Reservation Service.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from app.config import settings
from app.api.v1 import bookings
from app.database import Base, engine

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Booking & Reservation Service - Manages bookings and reservations across hotels, restaurants, cafes, and retail",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
# In development, allow all origins for easier testing
# In production, use specific origins from settings
cors_origins = ["*"] if settings.environment == "development" else settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bookings.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Create database tables (in production, use Alembic migrations)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except OperationalError as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.warning("Service will start but database operations will fail until connection is established")
        logger.info("To fix this, ensure PostgreSQL is running and the database/user are created:")
        logger.info("  CREATE DATABASE booking_reservation_db;")
        logger.info("  CREATE USER booking_user WITH PASSWORD 'booking_password';")
        logger.info("  GRANT ALL PRIVILEGES ON DATABASE booking_reservation_db TO booking_user;")
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
    
    # In production, start background tasks:
    # - Expire pending bookings
    # - Process payment confirmations
    # - Event consumer


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


