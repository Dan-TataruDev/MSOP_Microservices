"""
Main FastAPI application for the Feedback & Sentiment Analysis Service.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from sqlalchemy.exc import OperationalError

from app.config import settings
from app.api.v1 import feedback, insights, admin
from app.database import Base, engine
from app.events.handlers import register_handlers

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    # Create database tables (in production, use Alembic migrations)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except OperationalError as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.warning("Service will start but database operations will fail until connection is established")
        logger.info("To fix this, ensure PostgreSQL is running and the database/user are created:")
        logger.info("  CREATE DATABASE feedback_sentiment_db;")
        logger.info("  CREATE USER feedback_user WITH PASSWORD 'feedback_password';")
        logger.info("  GRANT ALL PRIVILEGES ON DATABASE feedback_sentiment_db TO feedback_user;")
        logger.info("Or use the default postgres user for development:")
        logger.info("  Set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/feedback_sentiment_db")
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
    
    register_handlers()
    logger.info("Feedback & Sentiment Analysis Service started")
    yield
    # Shutdown
    logger.info("Feedback & Sentiment Analysis Service shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Feedback & Sentiment Analysis Service
    
    Collects customer feedback and performs AI-powered sentiment analysis.
    
    ## Architecture
    - **Real-time**: Feedback submission (immediate response)
    - **Async/Batch**: Sentiment analysis (background processing)
    - **Graceful degradation**: Fallback when AI unavailable
    
    ## Consumers
    - Analytics Service: Aggregated insights
    - Marketing Service: Campaign targeting
    - Notification Service: Negative feedback alerts
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


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

