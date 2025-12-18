"""
Configuration management for the Dynamic Pricing Service.

This service calculates dynamic prices based on:
- Demand patterns
- Availability
- Seasonality
- Analytics insights
- AI/ML models
"""
from pydantic_settings import BaseSettings
from typing import List, Dict, Optional
from decimal import Decimal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "dynamic-pricing-service"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8008
    
    # Database
    # Default to SQLite for easy development (no setup required)
    # For PostgreSQL, set DATABASE_URL environment variable or create .env file
    database_url: str = "sqlite:///./dynamic_pricing.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Authentication
    auth_service_url: str = "http://localhost:8001"
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    
    # =========================================================================
    # AI/ML Pricing Engine Configuration
    # =========================================================================
    ai_provider: str = "openai"  # openai, azure, local, custom
    ai_api_key: str = ""
    ai_model: str = "gpt-4"
    ai_timeout_seconds: int = 30
    ai_max_retries: int = 3
    ai_retry_delay_seconds: int = 2
    
    # AI Confidence Thresholds
    ai_min_confidence_threshold: float = 0.7  # Below this, use fallback
    ai_price_deviation_max: float = 0.5  # Max 50% deviation from base price
    
    # =========================================================================
    # Fallback Pricing Configuration
    # =========================================================================
    fallback_enabled: bool = True
    fallback_strategy: str = "rule_based"  # rule_based, base_price, cached
    fallback_cache_ttl_seconds: int = 3600  # 1 hour cache for last known AI prices
    
    # =========================================================================
    # Pricing Rules & Boundaries
    # =========================================================================
    # Price floors and ceilings (multipliers of base price)
    price_floor_multiplier: float = 0.5  # Never go below 50% of base
    price_ceiling_multiplier: float = 3.0  # Never go above 300% of base
    
    # Demand surge thresholds
    high_demand_threshold: float = 0.8  # 80% occupancy
    low_demand_threshold: float = 0.3  # 30% occupancy
    
    # Surge pricing limits
    max_surge_multiplier: float = 2.0
    min_discount_multiplier: float = 0.7
    
    # =========================================================================
    # External Service URLs
    # =========================================================================
    inventory_service_url: str = "http://localhost:8003"
    analytics_service_url: str = "http://localhost:8006"
    booking_service_url: str = "http://localhost:8002"
    
    external_service_timeout: float = 10.0
    external_service_retry_attempts: int = 3
    
    # =========================================================================
    # Caching Configuration
    # =========================================================================
    cache_enabled: bool = True
    price_cache_ttl_seconds: int = 300  # 5 minutes
    demand_cache_ttl_seconds: int = 60  # 1 minute
    redis_url: str = "redis://localhost:6379/0"
    
    # =========================================================================
    # Event Streaming (RabbitMQ)
    # =========================================================================
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "hospitality_platform"
    rabbitmq_queue_prefix: str = "dynamic_pricing"
    
    # Event Topics
    event_topic_pricing: str = "pricing"
    event_topic_demand: str = "demand"
    event_topic_booking: str = "booking"
    event_topic_inventory: str = "inventory"
    
    # =========================================================================
    # Audit & Versioning
    # =========================================================================
    audit_enabled: bool = True
    audit_retention_days: int = 365  # Keep audit logs for 1 year
    price_decision_version_enabled: bool = True
    
    # =========================================================================
    # Rate Limiting
    # =========================================================================
    rate_limit_requests_per_minute: int = 1000
    rate_limit_ai_calls_per_minute: int = 60
    
    # =========================================================================
    # Tax Configuration
    # =========================================================================
    default_tax_rate: float = 0.10  # 10% default tax
    tax_included_in_price: bool = False
    
    # =========================================================================
    # Currency
    # =========================================================================
    default_currency: str = "USD"
    supported_currencies: List[str] = ["USD", "EUR", "GBP", "JPY", "AUD"]
    
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


