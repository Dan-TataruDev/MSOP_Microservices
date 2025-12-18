"""
Main FastAPI application for the Housekeeping & Maintenance Service.

This service manages operational tasks including:
- Cleaning schedules and task management
- Maintenance request tracking
- Staff workload balancing
- Operational dashboards and reporting

Integration Architecture:
- Consumes events from Booking Service (checkout triggers cleaning tasks)
- Consumes events from Inventory Service (low stock triggers restocking)
- Consumes events from Guest Interaction Service (complaints trigger maintenance)
- Publishes task completion events (room.ready, task.completed, task.delayed)
- Maintains its own database (no direct coupling to other service DBs)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api.v1 import tasks, schedules, maintenance, dashboard
from app.database import Base, engine
from app.events.handlers import register_handlers
from app.events.consumer import event_consumer
from sqlalchemy.exc import OperationalError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Housekeeping & Maintenance Service...")
    
    # Create database tables (in production, use Alembic migrations)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except OperationalError as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.warning("Service will start but database operations will fail until connection is established")
        logger.info("To fix this, ensure PostgreSQL is running and the database/user are created:")
        logger.info("  CREATE DATABASE housekeeping_db;")
        logger.info("  CREATE USER housekeeping_user WITH PASSWORD 'housekeeping_password';")
        logger.info("  GRANT ALL PRIVILEGES ON DATABASE housekeeping_db TO housekeeping_user;")
        logger.info("Or use the default postgres user for development:")
        logger.info("  Set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/housekeeping_db")
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
    
    register_handlers()
    # Start event consumer in background
    # await event_consumer.start_consuming()  # Uncomment when RabbitMQ is configured
    logger.info("Housekeeping & Maintenance Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Housekeeping & Maintenance Service...")
    logger.info("Housekeeping & Maintenance Service shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Housekeeping & Maintenance Service
    
    Manages operational tasks for hospitality operations including:
    
    ### Features
    - **Task Management**: Create, assign, track, and complete operational tasks
    - **Cleaning Schedules**: Define recurring cleaning patterns with time/event triggers
    - **Maintenance Requests**: Track maintenance issues from report to resolution
    - **Dashboard & Reporting**: Real-time operational metrics and historical reports
    
    ### Event-Driven Integration
    This service follows an event-driven architecture:
    
    **Consumed Events:**
    - `booking.completed` → Generates checkout cleaning task
    - `booking.cancelled` → Cancels scheduled tasks
    - `inventory.low_stock` → Generates restocking task
    - `inventory.critical_stock` → Generates urgent restocking task
    - `guest.complaint_filed` → May generate maintenance request
    
    **Published Events:**
    - `task.completed` → Notifies downstream services
    - `task.delayed` → Alerts about SLA breaches
    - `room.ready` → Signals room available for check-in
    - `maintenance.resolved` → Signals issue fixed
    
    ### Decoupling Strategy
    - No direct database connections to other services
    - Stores only reference IDs (venue_id, booking_reference)
    - Uses events for all inter-service communication
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(schedules.router, prefix="/api/v1")
app.include_router(maintenance.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """Health check endpoint for load balancers and orchestration."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


@app.get("/")
def root():
    """Root endpoint with service information."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "description": "Housekeeping & Maintenance Service",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/info")
def service_info():
    """Detailed service information."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "endpoints": {
            "tasks": "/api/v1/tasks",
            "schedules": "/api/v1/schedules",
            "maintenance": "/api/v1/maintenance",
            "dashboard": "/api/v1/dashboard"
        },
        "events": {
            "consumed": [
                "booking.completed",
                "booking.confirmed",
                "booking.cancelled",
                "inventory.low_stock",
                "inventory.critical_stock",
                "resource.room_status_changed",
                "guest.complaint_filed",
                "guest.maintenance_requested"
            ],
            "published": [
                "housekeeping.task.created",
                "housekeeping.task.assigned",
                "housekeeping.task.started",
                "housekeeping.task.completed",
                "housekeeping.task.delayed",
                "housekeeping.task.verified",
                "housekeeping.room.ready",
                "housekeeping.room.cleaning_started",
                "housekeeping.maintenance.reported",
                "housekeeping.maintenance.resolved",
                "housekeeping.maintenance.escalated",
                "housekeeping.alert.sla_breach",
                "housekeeping.alert.critical"
            ]
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
