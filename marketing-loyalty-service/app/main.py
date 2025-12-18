"""
Main FastAPI application for the Marketing & Loyalty Service.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api.v1 import campaigns, loyalty, offers
from app.database import Base, engine
from app.events.handlers import register_handlers
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting Marketing & Loyalty Service...")
    
    # Create database tables (in production, use Alembic migrations)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except OperationalError as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.warning("Service will start but database operations will fail until connection is established")
        logger.info("To fix this, ensure PostgreSQL is running and the database/user are created:")
        logger.info("  CREATE DATABASE marketing_loyalty_db;")
        logger.info("  CREATE USER marketing_user WITH PASSWORD 'marketing_password';")
        logger.info("  GRANT ALL PRIVILEGES ON DATABASE marketing_loyalty_db TO marketing_user;")
        logger.info("Or use the default postgres user for development:")
        logger.info("  Set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/marketing_loyalty_db")
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
    
    register_handlers()
    logger.info("Marketing & Loyalty Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Marketing & Loyalty Service shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Marketing & Loyalty Service
    
    Manages campaigns, promotions, loyalty programs, and targeted offers.
    
    ## Architecture
    
    This service acts as an **orchestration and decision layer**:
    - **Consumes insights** from personalization, sentiment, and analytics services
    - **Does NOT generate** those insights
    - **Does NOT embed** pricing calculations or booking rules
    - **Delegates** to respective services for final calculations
    
    ## Key Endpoints
    
    - `/api/v1/offers/eligible/{guest_id}` - Get personalized offers for frontend
    - `/api/v1/campaigns` - Manage marketing campaigns
    - `/api/v1/loyalty` - Loyalty program management
    
    ## Event Publishing
    
    Publishes engagement events for downstream analytics:
    - `offer.presented`, `offer.claimed`, `offer.redeemed`
    - `points.earned`, `tier.upgraded`
    - `campaign.created`, `campaign.activated`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campaigns.router, prefix="/api/v1")
app.include_router(loyalty.router, prefix="/api/v1")
app.include_router(offers.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name, "version": settings.app_version}


@app.get("/")
def root():
    """Root endpoint."""
    return {"service": settings.app_name, "version": settings.app_version, "docs": "/docs", "health": "/health"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)

