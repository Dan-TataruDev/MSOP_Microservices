"""
Configuration for Marketing & Loyalty Service.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "marketing-loyalty-service"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8008
    
    # Database
    # Default uses postgres user for development convenience
    # In production, use dedicated user: marketing_user:marketing_password
    database_url: str = "postgresql://postgres:postgres@localhost:5432/marketing_loyalty_db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # External Services (for consuming insights, NOT for pricing/booking rules)
    personalization_service_url: str = "http://localhost:8009"
    analytics_service_url: str = "http://localhost:8010"
    sentiment_service_url: str = "http://localhost:8007"
    
    # Event Streaming (RabbitMQ)
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "hospitality_platform"
    
    # Event Topics
    event_topic_campaigns: str = "campaigns"
    event_topic_loyalty: str = "loyalty"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

