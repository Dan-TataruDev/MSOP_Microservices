"""
Feedback service for handling feedback submission and retrieval.
"""
import logging
import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.feedback import Feedback, FeedbackStatus
from app.models.sentiment import SentimentAnalysis, AnalysisStatus
from app.schemas.feedback import FeedbackCreate, FeedbackResponse, SentimentSummary
from app.events.publisher import event_publisher
from app.config import settings

logger = logging.getLogger(__name__)


def generate_feedback_reference() -> str:
    """Generate unique feedback reference."""
    return f"FB-{uuid.uuid4().hex[:12].upper()}"


class FeedbackService:
    """
    Service for managing feedback submissions.
    
    Real-time operations: Submit feedback, get status
    Async operations: Sentiment analysis (handled by SentimentService)
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def submit_feedback(self, data: FeedbackCreate, guest_id: Optional[uuid.UUID] = None) -> Feedback:
        """
        Submit new feedback (real-time, non-blocking).
        
        Feedback is stored immediately and queued for async sentiment analysis.
        User receives immediate acknowledgment.
        """
        feedback_reference = generate_feedback_reference()
        
        feedback = Feedback(
            feedback_reference=feedback_reference,
            guest_id=guest_id,
            booking_id=data.booking_id,
            venue_id=data.venue_id,
            title=data.title,
            content=data.content,
            rating=data.rating,
            category=data.category,
            channel=data.channel,
            is_anonymous=data.is_anonymous,
            guest_email=data.guest_email if not data.is_anonymous else None,
            guest_name=data.guest_name if not data.is_anonymous else None,
            status=FeedbackStatus.RECEIVED,
            metadata=data.metadata,
        )
        
        # Create pending sentiment analysis record
        sentiment_analysis = SentimentAnalysis(
            feedback_id=feedback.id,
            status=AnalysisStatus.PENDING,
        )
        
        self.db.add(feedback)
        self.db.add(sentiment_analysis)
        self.db.commit()
        self.db.refresh(feedback)
        
        logger.info(f"Feedback submitted: {feedback_reference}")
        
        # Publish event for async processing
        event_publisher.publish_feedback_received(
            feedback_id=feedback.id,
            feedback_data={
                "reference": feedback_reference,
                "content_length": len(data.content),
                "has_rating": data.rating is not None,
            }
        )
        
        return feedback
    
    def get_feedback(self, feedback_id: uuid.UUID) -> Optional[Feedback]:
        """Get feedback by ID with sentiment if available."""
        return self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
    
    def get_feedback_by_reference(self, reference: str) -> Optional[Feedback]:
        """Get feedback by reference."""
        return self.db.query(Feedback).filter(Feedback.feedback_reference == reference).first()
    
    def list_feedback(
        self,
        venue_id: Optional[uuid.UUID] = None,
        status: Optional[FeedbackStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Feedback], int]:
        """List feedback with optional filters."""
        query = self.db.query(Feedback)
        
        if venue_id:
            query = query.filter(Feedback.venue_id == venue_id)
        if status:
            query = query.filter(Feedback.status == status)
        
        total = query.count()
        items = query.order_by(Feedback.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        return items, total
    
    def get_pending_analysis(self, limit: int = 50) -> List[Feedback]:
        """Get feedback items pending analysis (for batch processing)."""
        return (
            self.db.query(Feedback)
            .filter(Feedback.status == FeedbackStatus.RECEIVED)
            .order_by(Feedback.created_at.asc())
            .limit(limit)
            .all()
        )
    
    def to_response(self, feedback: Feedback) -> FeedbackResponse:
        """Convert feedback model to response schema."""
        sentiment_summary = None
        if feedback.sentiment_analysis and feedback.sentiment_analysis.status == AnalysisStatus.COMPLETED:
            sentiment_summary = SentimentSummary(
                sentiment=feedback.sentiment_analysis.sentiment,
                sentiment_score=feedback.sentiment_analysis.sentiment_score,
                confidence=feedback.sentiment_analysis.confidence,
                key_phrases=feedback.sentiment_analysis.key_phrases,
            )
        
        return FeedbackResponse(
            id=feedback.id,
            feedback_reference=feedback.feedback_reference,
            title=feedback.title,
            content=feedback.content,
            rating=feedback.rating,
            category=feedback.category,
            channel=feedback.channel,
            status=feedback.status,
            created_at=feedback.created_at,
            sentiment=sentiment_summary,
        )


