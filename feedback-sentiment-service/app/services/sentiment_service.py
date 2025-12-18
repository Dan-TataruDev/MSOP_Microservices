"""
Sentiment analysis service for async processing.
"""
import logging
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.feedback import Feedback, FeedbackStatus
from app.models.sentiment import SentimentAnalysis, AnalysisStatus, SentimentScore
from app.clients.sentiment_analyzer import get_sentiment_analyzer, SentimentResult
from app.events.publisher import event_publisher
from app.config import settings

logger = logging.getLogger(__name__)


class SentimentService:
    """
    Service for async sentiment analysis.
    
    Processes feedback in batches to avoid overwhelming AI services.
    Handles failures gracefully with retries and fallback.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.analyzer = get_sentiment_analyzer()
    
    def analyze_feedback(self, feedback: Feedback) -> Optional[SentimentAnalysis]:
        """
        Analyze single feedback item.
        
        This is the core analysis function called by batch processor.
        """
        analysis = feedback.sentiment_analysis
        if not analysis:
            logger.warning(f"No analysis record for feedback {feedback.id}")
            return None
        
        # Mark as processing
        analysis.status = AnalysisStatus.PROCESSING
        feedback.status = FeedbackStatus.ANALYZING
        self.db.commit()
        
        try:
            result, used_primary = self.analyzer.analyze(feedback.content, feedback.language)
            self._store_result(analysis, feedback, result, used_primary)
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis failed for {feedback.id}: {e}")
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            analysis.retry_count += 1
            feedback.status = FeedbackStatus.FAILED
            feedback.retry_count += 1
            feedback.last_retry_at = datetime.utcnow()
            self.db.commit()
            return None
    
    def _store_result(
        self,
        analysis: SentimentAnalysis,
        feedback: Feedback,
        result: SentimentResult,
        used_primary: bool,
    ) -> None:
        """Store analysis result."""
        analysis.sentiment = SentimentScore(result.sentiment_label)
        analysis.sentiment_score = result.sentiment_score
        analysis.confidence = result.confidence
        analysis.key_phrases = result.key_phrases
        analysis.emotions = result.emotions
        analysis.topics = result.topics
        analysis.aspect_sentiments = result.aspect_sentiments
        analysis.raw_response = result.raw_response
        analysis.model_used = result.model_used
        analysis.processing_time_ms = result.processing_time_ms
        analysis.status = AnalysisStatus.COMPLETED
        analysis.completed_at = datetime.utcnow()
        
        feedback.status = FeedbackStatus.ANALYZED
        feedback.analyzed_at = datetime.utcnow()
        
        self.db.commit()
        
        # Publish completion event
        event_publisher.publish_analysis_completed(
            feedback_id=feedback.id,
            analysis_data={
                "sentiment": result.sentiment_label,
                "score": result.sentiment_score,
                "used_fallback": not used_primary,
            }
        )
        
        logger.info(f"Analysis completed for {feedback.feedback_reference}: {result.sentiment_label}")
    
    def process_batch(self, batch_size: Optional[int] = None) -> int:
        """
        Process a batch of pending feedback items.
        
        This is called by background worker/scheduler.
        Returns number of items processed.
        """
        batch_size = batch_size or settings.batch_size
        
        pending = (
            self.db.query(Feedback)
            .filter(Feedback.status.in_([FeedbackStatus.RECEIVED, FeedbackStatus.FAILED]))
            .filter(Feedback.retry_count < settings.ai_max_retries)
            .order_by(Feedback.created_at.asc())
            .limit(batch_size)
            .all()
        )
        
        processed = 0
        for feedback in pending:
            try:
                self.analyze_feedback(feedback)
                processed += 1
            except Exception as e:
                logger.error(f"Batch processing error for {feedback.id}: {e}")
        
        logger.info(f"Batch processing completed: {processed}/{len(pending)} items")
        return processed
    
    def get_analysis(self, feedback_id) -> Optional[SentimentAnalysis]:
        """Get analysis for a feedback item."""
        return self.db.query(SentimentAnalysis).filter(SentimentAnalysis.feedback_id == feedback_id).first()


