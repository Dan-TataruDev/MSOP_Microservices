"""
Sentiment analysis database models.
"""
from sqlalchemy import Column, String, Float, DateTime, Text, Enum, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class SentimentScore(str, enum.Enum):
    """Overall sentiment classification."""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class AnalysisStatus(str, enum.Enum):
    """Analysis processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SentimentAnalysis(Base):
    """
    Stores AI-generated sentiment analysis results.
    
    Decoupled from feedback submission to allow async processing
    and graceful handling of AI service failures.
    """
    __tablename__ = "sentiment_analyses"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to feedback
    feedback_id = Column(UUID(as_uuid=True), ForeignKey("feedbacks.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Analysis status
    status = Column(Enum(AnalysisStatus), nullable=False, default=AnalysisStatus.PENDING, index=True)
    
    # Sentiment scores (normalized 0-1)
    sentiment = Column(Enum(SentimentScore), nullable=True)
    sentiment_score = Column(Float, nullable=True)  # -1 to 1 (negative to positive)
    confidence = Column(Float, nullable=True)  # 0 to 1
    
    # Detailed analysis
    key_phrases = Column(JSON, nullable=True)  # Extracted key phrases
    entities = Column(JSON, nullable=True)  # Named entities (staff names, locations, etc.)
    topics = Column(JSON, nullable=True)  # Detected topics/themes
    emotions = Column(JSON, nullable=True)  # Detected emotions (joy, anger, etc.)
    
    # Aspect-based sentiment (category-specific scores)
    aspect_sentiments = Column(JSON, nullable=True)  # {"service": 0.8, "cleanliness": -0.3}
    
    # AI metadata
    model_used = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    raw_response = Column(JSON, nullable=True)  # Full AI response for debugging
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Float, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    feedback = relationship("Feedback", back_populates="sentiment_analysis")
    
    __table_args__ = (
        Index("idx_sentiment_status", "status"),
        Index("idx_sentiment_score", "sentiment", "sentiment_score"),
    )


