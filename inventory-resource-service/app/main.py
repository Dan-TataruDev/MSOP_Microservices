"""Main FastAPI application for the Inventory & Resource Management Service."""
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from app.config import settings
from app.api.v1 import inventory, rooms, tables
from app.database import Base, engine
from app.events.handlers import register_handlers

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Inventory & Resource Management Service...")
    
    # Create database tables (in production, use Alembic migrations)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except OperationalError as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.warning("Service will start but database operations will fail until connection is established")
        logger.info("To fix this, ensure PostgreSQL is running and the database/user are created:")
        logger.info("  CREATE DATABASE inventory_db;")
        logger.info("  CREATE USER inventory_user WITH PASSWORD 'inventory_password';")
        logger.info("  GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;")
        logger.info("Or use the default postgres user for development:")
        logger.info("  Set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/inventory_db")
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
    
    register_handlers()
    logger.info("Inventory & Resource Management Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Inventory & Resource Management Service shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Inventory & Resource Management Service - Manages stock, rooms, tables, and resources",
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

app.include_router(inventory.router, prefix="/api/v1")
app.include_router(rooms.router, prefix="/api/v1")
app.include_router(tables.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name, "version": settings.app_version}


@app.get("/")
def root():
    """Root endpoint."""
    return {"service": settings.app_name, "version": settings.app_version, "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)

