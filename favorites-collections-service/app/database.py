"""
Database connection and session management.

Uses SQLAlchemy async engine with asyncpg driver for PostgreSQL.
Provides dependency injection for database sessions in FastAPI routes.
"""

from typing import AsyncGenerator
from urllib.parse import urlparse

import asyncpg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import get_settings

settings = get_settings()

# Create async engine with connection pooling
# echo=True logs SQL statements (useful for debugging, disable in production)
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    echo=settings.DEBUG,
)

# Session factory for creating new database sessions
# expire_on_commit=False prevents lazy loading issues after commit
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for all SQLAlchemy models
Base = declarative_base()


def _parse_database_url(url: str) -> dict:
    """
    Parse database URL to extract connection parameters.
    
    Format: postgresql+asyncpg://user:password@host:port/database
    """
    # Remove the +asyncpg part for parsing
    clean_url = url.replace("+asyncpg", "")
    parsed = urlparse(clean_url)
    
    return {
        "user": parsed.username or "postgres",
        "password": parsed.password or "",
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip("/") if parsed.path else "postgres",
    }


async def _ensure_database_exists() -> None:
    """
    Ensure the database exists, creating it if necessary.
    
    This is useful for development environments where the database
    might not have been created yet.
    """
    try:
        # Try to connect to the target database
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        # Database exists, nothing to do
        return
    except Exception:
        # Database doesn't exist, create it
        pass
    
    # Parse connection details
    db_params = _parse_database_url(settings.DATABASE_URL)
    target_db = db_params["database"]
    
    # Connect to postgres database (which always exists) using asyncpg directly
    # This is necessary because CREATE DATABASE cannot run in a transaction
    try:
        conn = await asyncpg.connect(
            host=db_params["host"],
            port=db_params["port"],
            user=db_params["user"],
            password=db_params["password"],
            database="postgres"  # Connect to postgres database
        )
        
        try:
            # Check if database exists
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1",
                target_db
            )
            
            if not exists:
                # Create the database
                await conn.execute(f'CREATE DATABASE "{target_db}"')
        finally:
            await conn.close()
    except Exception as e:
        # If we can't create the database (e.g., insufficient permissions),
        # log the error but don't fail - let the actual connection attempt fail
        # with a clearer error message
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not auto-create database {target_db}: {e}")
        logger.info(f"Please create the database manually: CREATE DATABASE {target_db};")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    
    Usage in FastAPI routes:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    
    The session is automatically closed after the request completes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    
    Creates the database if it doesn't exist, then creates all tables
    defined by models inheriting from Base.
    Safe to call multiple times - only creates tables that don't exist.
    """
    # Ensure database exists (for development convenience)
    await _ensure_database_exists()
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.
    
    Should be called during application shutdown to clean up resources.
    """
    await engine.dispose()

