"""
Database connection and session management for analytics.

Design Notes:
- Optimized for read-heavy workloads
- Separate from transactional databases to avoid interference
- Supports read replicas for horizontal scaling
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Primary database engine (for writes and reads)
engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
    echo=settings.debug,
)

# Read replica engine (optional, for scaling reads)
read_engine = None
if settings.read_replica_url:
    read_engine = create_engine(
        settings.read_replica_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,
        echo=settings.debug,
    )

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ReadSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=read_engine or engine
)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for write operations.
    Uses primary database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_read_db():
    """
    Dependency for read operations.
    Uses read replica if available, otherwise primary.
    Optimized for dashboard queries and report generation.
    """
    db = ReadSessionLocal()
    try:
        yield db
    finally:
        db.close()
