"""
Seed script for feedback-sentiment-service.
Generates feedback and sentiment analysis records.
"""
import sys
import os
from datetime import datetime, timedelta
import random
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.feedback import Feedback, FeedbackStatus, FeedbackChannel, FeedbackCategory
from app.models.sentiment import SentimentAnalysis, SentimentScore, AnalysisStatus

Base.metadata.create_all(bind=engine)

GUEST_IDS = [str(uuid.uuid4()) for _ in range(200)]
BOOKING_IDS = [str(uuid.uuid4()) for _ in range(1000)]
VENUE_IDS = [str(uuid.uuid4()) for _ in range(10)]

FEEDBACK_TEXTS = [
    "Great experience! The staff was very friendly and helpful.",
    "The room was clean and comfortable. Would definitely stay again.",
    "Excellent service and beautiful location. Highly recommended!",
    "The food was amazing and the atmosphere was perfect.",
    "Had a wonderful time. Everything exceeded our expectations.",
    "The service was slow and the room was not as described.",
    "Disappointed with the cleanliness. Found hair in the bathroom.",
    "The staff was rude and unhelpful. Very poor experience.",
    "The room was too small and the bed was uncomfortable.",
    "Overpriced for what you get. Not worth the money.",
    "Average experience. Nothing special but nothing terrible either.",
    "The location is good but the facilities need updating.",
    "Good value for money. Basic but clean and functional.",
    "The breakfast was included and was quite good.",
    "WiFi was slow and unreliable throughout the stay.",
    "Beautiful views from the room. Very peaceful location.",
    "The check-in process was smooth and efficient.",
    "Parking was difficult to find and expensive.",
    "The pool area was nice but could use more seating.",
    "Overall a pleasant stay. Would consider returning.",
]


def generate_feedback_reference(used_refs: set):
    """Generate a unique feedback reference."""
    while True:
        ref = f"FB{random.randint(100000, 999999)}"
        if ref not in used_refs:
            used_refs.add(ref)
            return ref


def generate_feedbacks(db: Session, num_feedbacks: int = 1500):
    """Generate feedback records."""
    print(f"Generating {num_feedbacks} feedbacks...")
    
    # Check existing references to avoid duplicates
    existing_refs = {ref[0] for ref in db.query(Feedback.feedback_reference).all()}
    used_refs = set(existing_refs)
    
    feedbacks = []
    for i in range(num_feedbacks):
        guest_id = random.choice(GUEST_IDS) if random.random() > 0.2 else None
        booking_id = random.choice(BOOKING_IDS) if random.random() > 0.3 else None
        venue_id = random.choice(VENUE_IDS) if random.random() > 0.1 else None
        
        content = random.choice(FEEDBACK_TEXTS)
        rating = random.randint(1, 5)
        category = random.choice(list(FeedbackCategory))
        channel = random.choice(list(FeedbackChannel))
        status = random.choice(list(FeedbackStatus))
        
        created_at = datetime.utcnow() - timedelta(days=random.randint(0, 180))
        analyzed_at = created_at + timedelta(hours=random.randint(1, 24)) if status == FeedbackStatus.ANALYZED else None
        
        feedback = Feedback(
            feedback_reference=generate_feedback_reference(used_refs),
            guest_id=uuid.UUID(guest_id) if guest_id else None,
            booking_id=uuid.UUID(booking_id) if booking_id else None,
            venue_id=uuid.UUID(venue_id) if venue_id else None,
            title=random.choice(["Great stay!", "Could be better", "Excellent service", "Disappointing", "Average experience", None]),
            content=content,
            rating=rating,
            category=category,
            channel=channel,
            is_anonymous=random.random() > 0.7,
            guest_email=f"guest{random.randint(1, 1000)}@example.com" if not random.random() > 0.7 else None,
            guest_name=f"Guest {random.randint(1, 1000)}" if not random.random() > 0.7 else None,
            status=status,
            language=random.choice(["en", "es", "fr", "de"]),
            created_at=created_at,
            analyzed_at=analyzed_at,
        )
        feedbacks.append(feedback)
    
    db.bulk_save_objects(feedbacks)
    db.commit()
    print(f"✓ Created {len(feedbacks)} feedbacks")
    return feedbacks


def generate_sentiment_analyses(db: Session, feedbacks: list):
    """Generate sentiment analysis records."""
    print("Generating sentiment analyses...")
    
    # Only analyze feedbacks that are analyzed
    analyzed_feedbacks = [f for f in feedbacks if f.status == FeedbackStatus.ANALYZED]
    
    analyses = []
    for feedback in analyzed_feedbacks:
        # Determine sentiment based on rating
        if feedback.rating >= 4:
            sentiment = random.choice([SentimentScore.POSITIVE, SentimentScore.VERY_POSITIVE])
            sentiment_score = random.uniform(0.6, 1.0)
        elif feedback.rating == 3:
            sentiment = SentimentScore.NEUTRAL
            sentiment_score = random.uniform(-0.2, 0.2)
        else:
            sentiment = random.choice([SentimentScore.NEGATIVE, SentimentScore.VERY_NEGATIVE])
            sentiment_score = random.uniform(-1.0, -0.2)
        
        analysis = SentimentAnalysis(
            feedback_id=feedback.id,
            status=AnalysisStatus.COMPLETED,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            confidence=random.uniform(0.7, 0.95),
            key_phrases=["service", "room", "staff", "location", "food"],
            entities={"location": "hotel", "staff": "friendly"},
            topics=["hospitality", "accommodation", "service quality"],
            emotions={"joy": 0.7 if sentiment_score > 0 else 0.2, "anger": 0.2 if sentiment_score < 0 else 0.1},
            aspect_sentiments={
                "service": random.uniform(-1.0, 1.0),
                "cleanliness": random.uniform(-1.0, 1.0),
                "value": random.uniform(-1.0, 1.0),
            },
            model_used="sentiment-analyzer-v2",
            model_version="2.1",
            processing_time_ms=random.uniform(100, 500),
            completed_at=feedback.analyzed_at,
        )
        analyses.append(analysis)
    
    db.bulk_save_objects(analyses)
    db.commit()
    print(f"✓ Created {len(analyses)} sentiment analyses")


def main():
    """Main function to seed the database."""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Seeding feedback-sentiment-service database...")
        print("=" * 60)
        
        feedbacks = generate_feedbacks(db, num_feedbacks=1500)
        generate_sentiment_analyses(db, feedbacks)
        
        print("=" * 60)
        print("✓ Database seeding completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

