"""Configuration management for the Housekeeping & Maintenance Service."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "housekeeping-maintenance-service"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8007
    
    # Database - Own isolated database (no direct coupling to other services)
    # Default uses postgres user for development convenience
    # In production, use dedicated user: housekeeping_user:housekeeping_password
    database_url: str = "postgresql://postgres:postgres@localhost:5432/housekeeping_db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Event Streaming (RabbitMQ) - Primary integration mechanism
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "hospitality_platform"
    rabbitmq_queue_prefix: str = "housekeeping"
    
    # Event Topics - Subscribed to for task generation
    event_topic_booking: str = "booking"
    event_topic_inventory: str = "inventory"
    event_topic_housekeeping: str = "housekeeping"
    
    # Task Configuration
    default_cleaning_duration_minutes: int = 45
    default_maintenance_duration_minutes: int = 60
    task_overdue_threshold_minutes: int = 30
    max_tasks_per_staff: int = 10
    
    # Priority Weights
    vip_priority_boost: int = 2
    urgent_maintenance_priority: int = 5
    
    # SLA Configuration (in minutes)
    checkout_cleaning_sla: int = 60
    maintenance_response_sla: int = 120
    critical_maintenance_sla: int = 30
    
    # Dashboard refresh interval
    dashboard_cache_ttl_seconds: int = 30
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
