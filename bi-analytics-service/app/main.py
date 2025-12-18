"""
Main FastAPI application for the Business Intelligence & Analytics Service.

Architecture Overview:
- Data Ingestion: Consumes events asynchronously from other services
- Metrics Computation: Pre-aggregates data for fast dashboard queries
- Read-Optimized: Uses caching, pre-computed aggregates, read replicas
- Eventual Consistency: Decoupled from transactional workloads
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.api.v1 import dashboards, reports, admin
from app.database import Base, engine
from app.events.consumer import event_consumer
from app.events.handlers import register_handlers
from sqlalchemy.exc import OperationalError

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Business Intelligence & Analytics Service...")
    
    # Create database tables (in production, use Alembic migrations)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except OperationalError as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.warning("Service will start but database operations will fail until connection is established")
        logger.info("To fix this, ensure PostgreSQL is running and the database/user are created:")
        logger.info("  CREATE DATABASE bi_analytics_db;")
        logger.info("  CREATE USER analytics_user WITH PASSWORD 'analytics_password';")
        logger.info("  GRANT ALL PRIVILEGES ON DATABASE bi_analytics_db TO analytics_user;")
        logger.info("Or use the default postgres user for development:")
        logger.info("  Set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bi_analytics_db")
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
    
    # Register event handlers
    register_handlers()
    
    # Start event consumer (in production, run as separate process)
    # event_consumer.start_consuming()
    
    logger.info(f"{settings.app_name} v{settings.app_version} started on port {settings.port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down BI Analytics Service...")
    event_consumer.stop_consuming()
    logger.info("Service stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## Business Intelligence & Analytics Service

Aggregates data from events emitted by other services to produce 
dashboards, reports, and KPIs for business users.

### Key Features

- **Real-time Dashboards**: Pre-aggregated KPIs updated every 5 minutes
- **Historical Reports**: Generate daily, weekly, monthly reports
- **Time Series Data**: Chart-ready data for trend analysis
- **Scheduled Reports**: Automatic report generation and distribution

### Architecture

- **Read-Heavy**: Optimized for fast metric retrieval
- **Eventually Consistent**: Accepts small lag in data freshness (5-15 min)
- **Non-Interfering**: Separate database from transactional services

### Event Sources

Consumes events from:
- Booking Service
- Payment Service
- Inventory Service
- Feedback Service
- Loyalty Service
- Housekeeping Service
- Dynamic Pricing Service
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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
app.include_router(dashboards.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(reports.router, prefix="/api/v1", tags=["reports"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])


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
    """Root endpoint with service information."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "description": "Business Intelligence & Analytics Service",
        "endpoints": {
            "dashboard": "/api/v1/dashboard",
            "metrics": "/api/v1/metrics/{metric_type}",
            "reports": "/api/v1/reports",
            "admin": "/api/v1/admin/stats",
            "docs": "/docs",
            "health": "/health",
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
