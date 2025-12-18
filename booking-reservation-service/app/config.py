"""
Configuration management for the Booking & Reservation Service.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "booking-reservation-service"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8002
    
    # Database
    database_url: str = "postgresql://booking_user:booking_password@localhost:5432/booking_reservation_db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Authentication
    auth_service_url: str = "http://localhost:8001"
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    
    # External Services (coordination, not embedding)
    inventory_service_url: str = "http://localhost:8003"
    pricing_service_url: str = "http://localhost:8004"
    payment_service_url: str = "http://localhost:8005"
    
    # Service timeouts (seconds)
    external_service_timeout: int = 5
    external_service_retry_attempts: int = 3
    
    # Event Streaming (RabbitMQ)
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "hospitality_platform"
    rabbitmq_queue_prefix: str = "booking_reservation"
    
    # Event Topics
    event_topic_booking: str = "booking"
    event_topic_reservation: str = "reservation"
    
    # Booking Configuration
    booking_confirmation_timeout_minutes: int = 15  # Time to confirm booking before auto-cancellation
    reservation_hold_timeout_minutes: int = 10  # Time to hold reservation before release
    max_booking_advance_days: int = 365  # Maximum days in advance for booking
    min_booking_advance_minutes: int = 30  # Minimum minutes in advance for booking
    
    # Conflict Resolution
    optimistic_locking_enabled: bool = True
    idempotency_key_ttl_hours: int = 24
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002"
    ]
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


