"""Configuration management for the Inventory & Resource Management Service."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "inventory-resource-service"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8006
    
    # Database
    # Default uses postgres user for development convenience
    # In production, use dedicated user: inventory_user:inventory_password
    database_url: str = "postgresql://postgres:postgres@localhost:5432/inventory_db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Event Streaming (RabbitMQ)
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "hospitality_platform"
    rabbitmq_queue_prefix: str = "inventory"
    
    # Event Topics
    event_topic_inventory: str = "inventory"
    event_topic_booking: str = "booking"
    event_topic_housekeeping: str = "housekeeping"
    event_topic_supplier: str = "supplier"
    
    # Threshold Settings
    default_low_stock_threshold: int = 10
    default_critical_stock_threshold: int = 5
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

