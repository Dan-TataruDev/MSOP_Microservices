"""
Insights service for aggregated analytics.
"""
import logging
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.feedback import Feedback, FeedbackStatus, FeedbackCategory
from app.models.sentiment import SentimentAnalysis, AnalysisStatus, SentimentScore
from app.schemas.insights import (
    InsightsSummary, SentimentDistribution, CategoryBreakdown,
    SentimentTrend, TopPhrase, VenueInsights
)

logger = logging.getLogger(__name__)


class InsightsService:
    """
    Service for generating aggregated insights.
    
    Designed for batch retrieval by analytics/marketing services.
    Results can be cached for performance.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_summary(
        self,
        venue_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> InsightsSummary:
        """Get aggregated insights summary."""
        start_date = start_date or datetime.utcnow() - timedelta(days=30)
        end_date = end_date or datetime.utcnow()
        
        # Base query
        base_filter = and_(
            Feedback.created_at >= start_date,
            Feedback.created_at <= end_date,
        )
        if venue_id:
            base_filter = and_(base_filter, Feedback.venue_id == venue_id)
        
        # Counts
        total = self.db.query(Feedback).filter(base_filter).count()
        analyzed = self.db.query(Feedback).filter(and_(base_filter, Feedback.status == FeedbackStatus.ANALYZED)).count()
        pending = self.db.query(Feedback).filter(and_(base_filter, Feedback.status == FeedbackStatus.RECEIVED)).count()
        
        # Sentiment distribution
        distribution = self._get_sentiment_distribution(base_filter)
        
        # Average sentiment
        avg_score = (
            self.db.query(func.avg(SentimentAnalysis.sentiment_score))
            .join(Feedback)
            .filter(base_filter)
            .filter(SentimentAnalysis.status == AnalysisStatus.COMPLETED)
            .scalar() or 0.0
        )
        
        # Category breakdown
        by_category = self._get_category_breakdown(base_filter)
        
        # Channel breakdown
        by_channel = dict(
            self.db.query(Feedback.channel, func.count(Feedback.id))
            .filter(base_filter)
            .group_by(Feedback.channel)
            .all()
        )
        
        # Trends
        trends = self._get_trends(base_filter, start_date, end_date)
        
        # Top phrases (simplified)
        top_positive, top_negative = self._get_top_phrases(base_filter)
        
        # Needs attention (very negative)
        needs_attention = (
            self.db.query(Feedback)
            .join(SentimentAnalysis)
            .filter(base_filter)
            .filter(SentimentAnalysis.sentiment == SentimentScore.VERY_NEGATIVE)
            .count()
        )
        
        return InsightsSummary(
            period_start=start_date,
            period_end=end_date,
            total_feedback_count=total,
            analyzed_count=analyzed,
            pending_count=pending,
            avg_sentiment_score=float(avg_score),
            sentiment_distribution=distribution,
            by_category=by_category,
            by_channel={str(k): v for k, v in by_channel.items()},
            trends=trends,
            top_positive_phrases=top_positive,
            top_negative_phrases=top_negative,
            common_topics=[],
            needs_attention_count=needs_attention,
        )
    
    def _get_sentiment_distribution(self, base_filter) -> SentimentDistribution:
        """Get distribution of sentiment scores."""
        counts = dict(
            self.db.query(SentimentAnalysis.sentiment, func.count(SentimentAnalysis.id))
            .join(Feedback)
            .filter(base_filter)
            .filter(SentimentAnalysis.status == AnalysisStatus.COMPLETED)
            .group_by(SentimentAnalysis.sentiment)
            .all()
        )
        
        return SentimentDistribution(
            very_negative=counts.get(SentimentScore.VERY_NEGATIVE, 0),
            negative=counts.get(SentimentScore.NEGATIVE, 0),
            neutral=counts.get(SentimentScore.NEUTRAL, 0),
            positive=counts.get(SentimentScore.POSITIVE, 0),
            very_positive=counts.get(SentimentScore.VERY_POSITIVE, 0),
        )
    
    def _get_category_breakdown(self, base_filter) -> List[CategoryBreakdown]:
        """Get sentiment breakdown by category."""
        results = (
            self.db.query(
                Feedback.category,
                func.count(Feedback.id),
                func.avg(SentimentAnalysis.sentiment_score),
            )
            .join(SentimentAnalysis, isouter=True)
            .filter(base_filter)
            .group_by(Feedback.category)
            .all()
        )
        
        return [
            CategoryBreakdown(
                category=str(cat) if cat else "unknown",
                count=count,
                avg_score=float(avg or 0),
                sentiment_distribution=SentimentDistribution(),
            )
            for cat, count, avg in results
        ]
    
    def _get_trends(self, base_filter, start_date: datetime, end_date: datetime) -> List[SentimentTrend]:
        """Get daily sentiment trends."""
        results = (
            self.db.query(
                func.date(Feedback.created_at).label("day"),
                func.avg(SentimentAnalysis.sentiment_score),
                func.count(Feedback.id),
            )
            .join(SentimentAnalysis, isouter=True)
            .filter(base_filter)
            .group_by(func.date(Feedback.created_at))
            .order_by(func.date(Feedback.created_at))
            .all()
        )
        
        return [
            SentimentTrend(
                period=str(day),
                avg_score=float(avg or 0),
                count=count,
                positive_pct=0.0,  # Simplified
                negative_pct=0.0,
            )
            for day, avg, count in results
        ]
    
    def _get_top_phrases(self, base_filter) -> tuple[List[TopPhrase], List[TopPhrase]]:
        """Get top positive and negative phrases."""
        # Simplified - in production, aggregate from key_phrases JSON field
        return [], []
    
    def get_venue_insights(self, venue_id: UUID) -> VenueInsights:
        """Get insights for a specific venue with comparison."""
        summary = self.get_summary(venue_id=venue_id)
        
        # Get overall average for comparison
        overall_avg = (
            self.db.query(func.avg(SentimentAnalysis.sentiment_score))
            .filter(SentimentAnalysis.status == AnalysisStatus.COMPLETED)
            .scalar() or 0.0
        )
        
        comparison = summary.avg_sentiment_score - float(overall_avg)
        
        return VenueInsights(
            venue_id=venue_id,
            summary=summary,
            comparison_to_avg=comparison,
        )


