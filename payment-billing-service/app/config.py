"""
Configuration management for the Payment & Billing Service.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "payment-billing-service"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8005
    
    # Database
    # Default uses postgres user for development convenience
    # In production, use dedicated user: payment_user:payment_password
    database_url: str = "postgresql://postgres:postgres@localhost:5432/payment_billing_db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Authentication
    auth_service_url: str = "http://localhost:8001"
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    
    # External Payment Providers (abstracted)
    payment_provider: str = "stripe"  # stripe, paypal, square, etc.
    payment_provider_api_key: str = ""
    payment_provider_secret_key: str = ""
    payment_provider_webhook_secret: str = ""
    
    # Payment Configuration
    payment_timeout_seconds: int = 30
    payment_retry_attempts: int = 3
    payment_retry_delay_seconds: int = 5
    payment_confirmation_timeout_minutes: int = 15
    
    # Refund Configuration
    refund_timeout_seconds: int = 30
    refund_retry_attempts: int = 3
    auto_refund_on_cancellation: bool = True
    
    # Invoice Configuration
    invoice_number_prefix: str = "INV"
    invoice_due_days: int = 30
    invoice_currency: str = "USD"
    
    # Service timeouts (seconds)
    external_service_timeout: int = 5
    external_service_retry_attempts: int = 3
    
    # Event Streaming (RabbitMQ)
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "hospitality_platform"
    rabbitmq_queue_prefix: str = "payment_billing"
    
    # Event Topics
    event_topic_payment: str = "payment"
    event_topic_booking: str = "booking"  # For consuming booking events
    
    # Data Protection
    encrypt_sensitive_data: bool = True
    sensitive_data_retention_days: int = 365
    
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

