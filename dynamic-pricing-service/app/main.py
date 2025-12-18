"""
Main FastAPI application for the Dynamic Pricing Service.

This service calculates dynamic prices based on:
- Demand patterns
- Availability
- Seasonality
- Analytics insights
- AI/ML models

It does NOT own bookings or payments - only pricing logic.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app.config import settings
from app.database import Base, engine
from app.api.v1 import (
    pricing_router,
    rules_router,
    decisions_router,
    base_prices_router,
)
from app.events.consumer import EventConsumer
from app.events.handlers import PricingEventHandlers

logger = logging.getLogger(__name__)

# Event consumer instance
event_consumer = EventConsumer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    # Create database tables (in production, use Alembic migrations)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except OperationalError as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.warning("Service will start but database operations will fail until connection is established")
        logger.info("To fix this, ensure PostgreSQL is running and the database/user are created:")
        logger.info("  CREATE DATABASE dynamic_pricing_db;")
        logger.info("  CREATE USER pricing_user WITH PASSWORD 'pricing_password';")
        logger.info("  GRANT ALL PRIVILEGES ON DATABASE dynamic_pricing_db TO pricing_user;")
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
    
    # Register event handlers and start consumer
    PricingEventHandlers.register_all(event_consumer)
    event_consumer.start()
    
    yield
    
    # Shutdown
    event_consumer.stop()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## Dynamic Pricing Service

AI-driven pricing engine for the hospitality platform.

### Features

- **Dynamic Price Calculation**: Calculates optimal prices based on demand, 
  seasonality, time of day, and AI/ML models.
  
- **Rule-Based Pricing**: Configurable pricing rules for seasonal adjustments,
  promotions, and loyalty discounts.
  
- **Fallback Mechanisms**: Graceful degradation when AI is unavailable with
  rule-based and cached price fallbacks.
  
- **Full Auditability**: Every price decision is versioned and logged for
  compliance and analytics.

### API Groups

- **Pricing**: Calculate and estimate prices for bookings
- **Rules**: Manage pricing rules (seasonal, demand, promotional)
- **Decisions**: Query and audit price decisions
- **Base Prices**: Manage base prices for venues and products

### Integration

This service is called by the Booking Service to get prices. It coordinates
with Inventory Service (availability) and Analytics Service (demand signals)
but does NOT own bookings or payments.
    """,
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
app.include_router(pricing_router, prefix="/api/v1")
app.include_router(rules_router, prefix="/api/v1")
app.include_router(decisions_router, prefix="/api/v1")
app.include_router(base_prices_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/health/detailed")
def detailed_health_check():
    """Detailed health check with component status."""
    from app.services.rule_service import RuleService
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        rule_service = RuleService(db)
        active_rules = rule_service.get_active_rules_count()
        
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "components": {
                "database": "connected",
                "active_rules": active_rules,
                "ai_provider": settings.ai_provider,
                "fallback_enabled": settings.fallback_enabled,
            }
        }
    finally:
        db.close()


@app.get("/")
def root():
    """Root endpoint with service info."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "description": "Dynamic Pricing Service - AI-driven pricing engine",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "calculate_price": "POST /api/v1/pricing/calculate",
            "estimate_price": "POST /api/v1/pricing/estimate",
            "manage_rules": "/api/v1/rules",
            "query_decisions": "/api/v1/decisions",
            "manage_base_prices": "/api/v1/base-prices",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


