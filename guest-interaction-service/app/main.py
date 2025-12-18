"""
Main FastAPI application for the Guest Interaction & Personalization Service.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from sqlalchemy.exc import OperationalError
from app.config import settings
from app.api.v1 import guests, preferences, interactions, personalization, venues
from app.api.v1.preferences import categories_router
from app.events.handlers import setup_event_handlers
from app.database import Base, engine

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Guest Interaction & Personalization Service - Manages guest profiles, preferences, and personalization data",
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
app.include_router(guests.router)
app.include_router(preferences.router)
app.include_router(categories_router)
app.include_router(interactions.router)
app.include_router(personalization.router)
app.include_router(venues.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Guest Interaction & Personalization Service...")
    
    # Create database tables (in production, use Alembic migrations)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except OperationalError as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.warning("Service will start but database operations will fail until connection is established")
        logger.info("To fix this, ensure PostgreSQL is running and the database/user are created:")
        logger.info("  CREATE DATABASE guest_interaction_db;")
        logger.info("  CREATE USER guest_user WITH PASSWORD 'guest_password';")
        logger.info("  GRANT ALL PRIVILEGES ON DATABASE guest_interaction_db TO guest_user;")
        logger.info("Or use the default postgres user for development:")
        logger.info("  Set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/guest_interaction_db")
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
    
    # Setup event handlers
    setup_event_handlers()
    
    # In production, start event consumer
    # from app.events.consumer import event_consumer
    # event_consumer.start_consuming()
    
    logger.info(f"{settings.app_name} v{settings.app_version} started on port {settings.port}")


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
