"""
Admin API endpoints for manual processing triggers.
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.sentiment_service import SentimentService
from app.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/process-batch")
def trigger_batch_processing(
    background_tasks: BackgroundTasks,
    batch_size: int = settings.batch_size,
    db: Session = Depends(get_db),
):
    """
    Manually trigger batch processing of pending feedback.
    
    In production, this is called by a scheduler.
    """
    def process():
        service = SentimentService(db)
        return service.process_batch(batch_size)
    
    background_tasks.add_task(process)
    return {"message": "Batch processing triggered", "batch_size": batch_size}


@router.get("/stats")
def get_processing_stats(db: Session = Depends(get_db)):
    """Get current processing statistics."""
    from app.models.feedback import Feedback, FeedbackStatus
    from sqlalchemy import func
    
    stats = dict(
        db.query(Feedback.status, func.count(Feedback.id))
        .group_by(Feedback.status)
        .all()
    )
    
    return {
        "received": stats.get(FeedbackStatus.RECEIVED, 0),
        "analyzing": stats.get(FeedbackStatus.ANALYZING, 0),
        "analyzed": stats.get(FeedbackStatus.ANALYZED, 0),
        "failed": stats.get(FeedbackStatus.FAILED, 0),
    }


