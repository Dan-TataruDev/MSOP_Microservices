"""
AI Sentiment Analyzer client with graceful failure handling.

Supports multiple providers (OpenAI, Azure, local models) with fallback.
"""
import logging
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from app.config import settings

logger = logging.getLogger(__name__)


class SentimentResult:
    """Standardized sentiment analysis result."""
    def __init__(
        self,
        sentiment_score: float,  # -1 to 1
        confidence: float,
        key_phrases: list,
        emotions: dict,
        topics: list,
        aspect_sentiments: dict,
        raw_response: dict,
        model_used: str,
        processing_time_ms: float,
    ):
        self.sentiment_score = sentiment_score
        self.confidence = confidence
        self.key_phrases = key_phrases
        self.emotions = emotions
        self.topics = topics
        self.aspect_sentiments = aspect_sentiments
        self.raw_response = raw_response
        self.model_used = model_used
        self.processing_time_ms = processing_time_ms
    
    @property
    def sentiment_label(self) -> str:
        """Convert score to label."""
        if self.sentiment_score <= -0.6:
            return "very_negative"
        elif self.sentiment_score <= -0.2:
            return "negative"
        elif self.sentiment_score <= 0.2:
            return "neutral"
        elif self.sentiment_score <= 0.6:
            return "positive"
        return "very_positive"


class SentimentAnalyzer(ABC):
    """Abstract base class for sentiment analyzers."""
    
    @abstractmethod
    def analyze(self, text: str, language: str = "en") -> SentimentResult:
        """Analyze text and return sentiment result."""
        pass


class OpenAISentimentAnalyzer(SentimentAnalyzer):
    """OpenAI-based sentiment analyzer."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        # In production: initialize OpenAI client
        logger.info(f"OpenAI analyzer initialized with model: {model}")
    
    def analyze(self, text: str, language: str = "en") -> SentimentResult:
        """Analyze text using OpenAI."""
        start_time = time.time()
        
        # In production, call OpenAI API:
        # response = openai.ChatCompletion.create(...)
        
        # Simulated response for development
        logger.info(f"Analyzing text ({len(text)} chars) with OpenAI")
        
        # Mock analysis result
        result = SentimentResult(
            sentiment_score=0.0,  # Would come from AI
            confidence=0.85,
            key_phrases=["service", "staff", "experience"],
            emotions={"satisfaction": 0.7, "frustration": 0.1},
            topics=["customer service", "hospitality"],
            aspect_sentiments={"service": 0.5, "cleanliness": 0.3},
            raw_response={"mock": True},
            model_used=self.model,
            processing_time_ms=(time.time() - start_time) * 1000,
        )
        
        return result


class FallbackSentimentAnalyzer(SentimentAnalyzer):
    """
    Simple rule-based fallback analyzer.
    
    Used when AI service is unavailable to provide basic analysis.
    """
    
    POSITIVE_WORDS = {"great", "excellent", "amazing", "wonderful", "fantastic", "love", "best", "happy", "clean", "friendly"}
    NEGATIVE_WORDS = {"bad", "terrible", "awful", "worst", "dirty", "rude", "slow", "disappointed", "poor", "horrible"}
    
    def analyze(self, text: str, language: str = "en") -> SentimentResult:
        """Basic keyword-based sentiment analysis."""
        start_time = time.time()
        words = text.lower().split()
        
        positive_count = sum(1 for w in words if w in self.POSITIVE_WORDS)
        negative_count = sum(1 for w in words if w in self.NEGATIVE_WORDS)
        total = positive_count + negative_count
        
        if total == 0:
            score = 0.0
        else:
            score = (positive_count - negative_count) / total
        
        return SentimentResult(
            sentiment_score=score,
            confidence=0.5,  # Lower confidence for fallback
            key_phrases=[],
            emotions={},
            topics=[],
            aspect_sentiments={},
            raw_response={"fallback": True, "positive": positive_count, "negative": negative_count},
            model_used="fallback_rule_based",
            processing_time_ms=(time.time() - start_time) * 1000,
        )


class ResilientSentimentAnalyzer:
    """
    Wrapper that handles AI failures gracefully with retries and fallback.
    """
    
    def __init__(self, primary: SentimentAnalyzer, fallback: SentimentAnalyzer):
        self.primary = primary
        self.fallback = fallback
        self.max_retries = settings.ai_max_retries
        self.retry_delay = settings.ai_retry_delay_seconds
    
    def analyze(self, text: str, language: str = "en") -> tuple[SentimentResult, bool]:
        """
        Analyze with retry and fallback.
        
        Returns: (result, used_primary) - result and whether primary analyzer was used
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = self.primary.analyze(text, language)
                return result, True
            except Exception as e:
                last_error = e
                logger.warning(f"AI analysis attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        # All retries failed, use fallback
        logger.warning(f"AI analysis failed after {self.max_retries} attempts, using fallback")
        if settings.ai_failure_fallback:
            return self.fallback.analyze(text, language), False
        
        raise last_error


def get_sentiment_analyzer() -> ResilientSentimentAnalyzer:
    """Factory function to get configured sentiment analyzer."""
    primary = OpenAISentimentAnalyzer(
        api_key=settings.ai_api_key,
        model=settings.ai_model,
    )
    fallback = FallbackSentimentAnalyzer()
    return ResilientSentimentAnalyzer(primary, fallback)


