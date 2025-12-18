"""
Insights Pydantic schemas for analytics and reporting APIs.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
from app.models.sentiment import SentimentScore


class SentimentDistribution(BaseModel):
    """Distribution of sentiment scores."""
    very_negative: int = 0
    negative: int = 0
    neutral: int = 0
    positive: int = 0
    very_positive: int = 0


class CategoryBreakdown(BaseModel):
    """Sentiment breakdown by category."""
    category: str
    count: int
    avg_score: float
    sentiment_distribution: SentimentDistribution


class SentimentTrend(BaseModel):
    """Time-series sentiment data point."""
    period: str  # Date or period label
    avg_score: float
    count: int
    positive_pct: float
    negative_pct: float


class TopPhrase(BaseModel):
    """Frequently mentioned phrase with sentiment."""
    phrase: str
    count: int
    avg_sentiment: float


class InsightsSummary(BaseModel):
    """
    Aggregated insights for analytics/marketing services.
    
    This is the main response for analytics consumers.
    Designed for batch retrieval, not real-time.
    """
    period_start: datetime
    period_end: datetime
    
    # Overview metrics
    total_feedback_count: int
    analyzed_count: int
    pending_count: int
    
    # Sentiment overview
    avg_sentiment_score: float
    sentiment_distribution: SentimentDistribution
    
    # Breakdowns
    by_category: List[CategoryBreakdown]
    by_channel: Dict[str, int]
    
    # Trends (daily/weekly)
    trends: List[SentimentTrend]
    
    # Key insights
    top_positive_phrases: List[TopPhrase]
    top_negative_phrases: List[TopPhrase]
    common_topics: List[str]
    
    # Actionable items
    needs_attention_count: int  # Very negative feedback requiring follow-up


class VenueInsights(BaseModel):
    """Insights scoped to a specific venue."""
    venue_id: UUID
    summary: InsightsSummary
    comparison_to_avg: float  # vs overall platform average


class InsightsQuery(BaseModel):
    """Query parameters for insights retrieval."""
    venue_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    categories: Optional[List[str]] = None
    min_rating: Optional[int] = None


