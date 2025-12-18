"""
Main FastAPI application for the Payment & Billing Service.
"""
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from app.config import settings
from app.api.v1 import payments, billing, invoices, refunds
from app.database import Base, engine
from app.events.consumer import event_consumer
from app.events.handlers import register_handlers

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Payment & Billing Service...")
    
    # Create database tables (in production, use Alembic migrations)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except OperationalError as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.warning("Service will start but database operations will fail until connection is established")
        logger.info("To fix this, ensure PostgreSQL is running and the database/user are created:")
        logger.info("  CREATE DATABASE payment_billing_db;")
        logger.info("  CREATE USER payment_user WITH PASSWORD 'payment_password';")
        logger.info("  GRANT ALL PRIVILEGES ON DATABASE payment_billing_db TO payment_user;")
        logger.info("Or use the default postgres user for development:")
        logger.info("  Set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/payment_billing_db")
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
    
    # Register event handlers
    register_handlers()
    
    # In production, start background tasks:
    # - Event consumer for booking events
    # - Payment status reconciliation
    # - Webhook processing
    logger.info("Payment & Billing Service started successfully")
    
    yield
    
    # Shutdown
    # Close event consumer connections
    logger.info("Payment & Billing Service shutting down")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Payment & Billing Service - Handles payment processing, billing records, refunds, and invoicing",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(payments.router, prefix="/api/v1", tags=["payments"])
app.include_router(billing.router, prefix="/api/v1", tags=["billing"])
app.include_router(invoices.router, prefix="/api/v1", tags=["invoices"])
app.include_router(refunds.router, prefix="/api/v1", tags=["refunds"])


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
    import logging
    
    logger = logging.getLogger(__name__)
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )

