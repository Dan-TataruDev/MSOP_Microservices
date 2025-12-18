"""
Configuration settings for the Favorites & Collections Service.

Uses pydantic-settings for environment variable management with sensible defaults.
All sensitive values should be provided via environment variables in production.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application metadata
    APP_NAME: str = "Favorites & Collections Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8007
    
    # Database configuration
    # Format: postgresql+asyncpg://user:password@host:port/database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/favorites_collections_db"
    
    # Connection pool settings
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # JWT Authentication
    # In production, this should be a shared secret or public key from the auth service
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Feature flags
    ENABLE_SOFT_DELETE: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Using lru_cache ensures settings are loaded once and reused,
    avoiding repeated environment variable lookups.
    """
    return Settings()


