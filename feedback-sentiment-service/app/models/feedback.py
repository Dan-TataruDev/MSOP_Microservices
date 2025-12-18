"""
Feedback database models.
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum, Index, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class FeedbackStatus(str, enum.Enum):
    """Feedback processing status."""
    RECEIVED = "received"  # Feedback received, awaiting analysis
    ANALYZING = "analyzing"  # AI analysis in progress
    ANALYZED = "analyzed"  # Analysis complete
    FAILED = "failed"  # Analysis failed, will retry


class FeedbackChannel(str, enum.Enum):
    """Channel through which feedback was submitted."""
    WEB = "web"
    MOBILE = "mobile"
    EMAIL = "email"
    KIOSK = "kiosk"
    SURVEY = "survey"
    SOCIAL = "social"


class FeedbackCategory(str, enum.Enum):
    """Pre-defined feedback categories."""
    SERVICE = "service"
    CLEANLINESS = "cleanliness"
    AMENITIES = "amenities"
    FOOD = "food"
    LOCATION = "location"
    VALUE = "value"
    STAFF = "staff"
    GENERAL = "general"


class Feedback(Base):
    """
    Main feedback entity capturing customer feedback submissions.
    
    Design: Feedback is stored immediately (real-time) while sentiment
    analysis happens asynchronously to avoid blocking user flows.
    """
    __tablename__ = "feedbacks"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Feedback identification
    feedback_reference = Column(String(50), unique=True, nullable=False, index=True)
    
    # Related entities (references, not foreign keys - service isolation)
    guest_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    booking_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    venue_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Feedback content
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 star rating if provided
    category = Column(Enum(FeedbackCategory), nullable=True, default=FeedbackCategory.GENERAL)
    
    # Submission metadata
    channel = Column(Enum(FeedbackChannel), nullable=False, default=FeedbackChannel.WEB)
    is_anonymous = Column(Boolean, default=False)
    guest_email = Column(String(255), nullable=True)
    guest_name = Column(String(255), nullable=True)
    
    # Processing status
    status = Column(Enum(FeedbackStatus), nullable=False, default=FeedbackStatus.RECEIVED, index=True)
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional data
    extra_data = Column(JSON, nullable=True)  # Custom fields, tags, etc.
    language = Column(String(10), default="en")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    analyzed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship to sentiment analysis
    sentiment_analysis = relationship("SentimentAnalysis", back_populates="feedback", uselist=False)
    
    __table_args__ = (
        Index("idx_feedback_status_created", "status", "created_at"),
        Index("idx_feedback_venue_created", "venue_id", "created_at"),
        Index("idx_feedback_guest", "guest_id", "created_at"),
    )
