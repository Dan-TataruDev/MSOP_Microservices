"""
Configuration management for the Guest Interaction Service.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "guest-interaction-service"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "postgresql://guest_user:guest_password@localhost:5432/guest_interaction_db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Authentication
    auth_service_url: str = "http://localhost:8001"
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    
    # Event Streaming (RabbitMQ)
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "hospitality_platform"
    rabbitmq_queue_prefix: str = "guest_interaction"
    
    # Event Topics
    event_topic_booking: str = "booking"
    event_topic_feedback: str = "feedback"
    event_topic_marketing: str = "marketing"
    event_topic_order: str = "order"
    
    # GDPR and Privacy
    data_retention_days: int = 2555  # 7 years
    anonymization_enabled: bool = True
    audit_log_enabled: bool = True
    
    # CORS
    # For development, allow all localhost ports
    # In production, specify exact origins
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:5173",  # Vite default port
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ]
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
