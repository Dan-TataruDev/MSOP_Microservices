"""
Configuration management for the Business Intelligence & Analytics Service.

Design Principles:
- Read-heavy: Optimized for fast metric retrieval
- Eventual consistency: Accepts lag in data freshness
- Non-interference: Separate from transactional databases
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "bi-analytics-service"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8010
    
    # Analytics Database (separate from transactional DBs)
    # Using a dedicated read-optimized database
    # Default uses postgres user for development convenience
    # In production, use dedicated user: analytics_user:analytics_password
    database_url: str = "postgresql://postgres:postgres@localhost:5432/bi_analytics_db"
    database_pool_size: int = 20  # Higher pool for read-heavy workload
    database_max_overflow: int = 40
    
    # Read Replica (for scaling reads)
    read_replica_url: str = ""  # Optional: separate read replica
    
    # Caching (Redis for frequently accessed metrics)
    redis_url: str = "redis://localhost:6379/1"
    cache_ttl_seconds: int = 300  # 5 minutes default TTL
    cache_kpi_ttl_seconds: int = 60  # 1 minute for real-time KPIs
    
    # Event Streaming (RabbitMQ)
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "hospitality_platform"
    rabbitmq_queue_prefix: str = "bi_analytics"
    
    # Event Topics to Subscribe (all services)
    event_topics: List[str] = [
        "booking",
        "payment",
        "inventory",
        "feedback",
        "loyalty",
        "housekeeping",
        "pricing",
    ]
    
    # Aggregation Settings
    aggregation_interval_minutes: int = 5  # Re-aggregate every 5 minutes
    retention_days_raw: int = 90  # Keep raw events for 90 days
    retention_days_hourly: int = 365  # Keep hourly aggregates for 1 year
    retention_days_daily: int = 1825  # Keep daily aggregates for 5 years
    
    # Batch Processing
    batch_size: int = 1000  # Events per batch for aggregation
    max_concurrent_aggregations: int = 4
    
    # Authentication
    auth_service_url: str = "http://localhost:8001"
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
    ]
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
