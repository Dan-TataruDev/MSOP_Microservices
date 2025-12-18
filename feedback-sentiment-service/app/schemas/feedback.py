"""
Feedback Pydantic schemas for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.feedback import FeedbackStatus, FeedbackChannel, FeedbackCategory
from app.models.sentiment import SentimentScore


class FeedbackCreate(BaseModel):
    """Schema for submitting feedback (real-time, non-blocking)."""
    content: str = Field(..., min_length=10, max_length=5000)
    title: Optional[str] = Field(None, max_length=255)
    rating: Optional[int] = Field(None, ge=1, le=5)
    category: Optional[FeedbackCategory] = FeedbackCategory.GENERAL
    channel: FeedbackChannel = FeedbackChannel.WEB
    booking_id: Optional[UUID] = None
    venue_id: Optional[UUID] = None
    guest_email: Optional[str] = None
    guest_name: Optional[str] = None
    is_anonymous: bool = False
    metadata: Optional[Dict[str, Any]] = None


class SentimentSummary(BaseModel):
    """Embedded sentiment summary in feedback response."""
    sentiment: Optional[SentimentScore] = None
    sentiment_score: Optional[float] = None
    confidence: Optional[float] = None
    key_phrases: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class FeedbackResponse(BaseModel):
    """Schema for feedback response (immediate acknowledgment)."""
    id: UUID
    feedback_reference: str
    title: Optional[str]
    content: str
    rating: Optional[int]
    category: Optional[FeedbackCategory]
    channel: FeedbackChannel
    status: FeedbackStatus
    created_at: datetime
    # Sentiment included only if analysis is complete
    sentiment: Optional[SentimentSummary] = None
    
    class Config:
        from_attributes = True


class FeedbackListResponse(BaseModel):
    """Schema for paginated feedback list."""
    items: List[FeedbackResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class FeedbackStatusResponse(BaseModel):
    """Schema for checking feedback analysis status."""
    feedback_reference: str
    status: FeedbackStatus
    sentiment: Optional[SentimentSummary] = None
    analyzed_at: Optional[datetime] = None


