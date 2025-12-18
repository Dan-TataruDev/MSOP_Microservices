"""
Configuration management for the Feedback & Sentiment Analysis Service.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "feedback-sentiment-service"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8007
    
    # Database
    # Default uses postgres user for development convenience
    # In production, use dedicated user: feedback_user:feedback_password
    database_url: str = "postgresql://postgres:postgres@localhost:5432/feedback_sentiment_db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Authentication
    auth_service_url: str = "http://localhost:8001"
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    
    # AI/Sentiment Analysis Configuration
    ai_provider: str = "openai"  # openai, azure, local
    ai_api_key: str = ""
    ai_model: str = "gpt-3.5-turbo"
    ai_timeout_seconds: int = 30
    ai_max_retries: int = 3
    ai_retry_delay_seconds: int = 2
    
    # Processing Configuration
    batch_size: int = 50  # Batch processing size
    batch_interval_seconds: int = 60  # How often to run batch processing
    analysis_queue_max_size: int = 1000
    
    # Graceful Degradation
    ai_failure_fallback: bool = True  # Store feedback even if AI fails
    max_pending_analysis_age_hours: int = 24  # Re-queue old pending items
    
    # Event Streaming (RabbitMQ)
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "hospitality_platform"
    rabbitmq_queue_prefix: str = "feedback_sentiment"
    
    # Event Topics
    event_topic_feedback: str = "feedback"
    event_topic_insights: str = "insights"
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002"
    ]
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

