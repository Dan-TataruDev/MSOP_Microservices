"""
Event handlers for consuming events from other services.
"""
import logging
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.events.consumer import event_consumer
from app.services.interaction_service import InteractionService
from app.services.preference_service import PreferenceService
from app.models.interaction import InteractionType
from app.config import settings

logger = logging.getLogger(__name__)


def handle_booking_created(payload: Dict[str, Any]) -> None:
    """Handle booking.created event from booking service."""
    db = SessionLocal()
    try:
        guest_id = UUID(payload.get("user_id"))  # Assuming user_id maps to guest_id
        booking_id = payload.get("booking_id")
        venue_id = payload.get("venue_id")
        
        # Find or create interaction type
        interaction_type = InteractionService.get_interaction_type_by_name(
            db, "booking_created"
        )
        if not interaction_type:
            logger.warning("Interaction type 'booking_created' not found")
            return
        
        # Record interaction
        from app.schemas.interaction import InteractionCreate
        interaction_data = InteractionCreate(
            interaction_type_id=interaction_type.id,
            entity_type="booking",
            entity_id=booking_id,
            context={"venue_id": venue_id},
            source="booking_service",
            source_event_id=payload.get("event_id"),
        )
        
        InteractionService.create_interaction(db, guest_id, interaction_data)
        logger.info(f"Recorded booking interaction for guest {guest_id}")
    except Exception as e:
        logger.error(f"Error handling booking.created event: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def handle_booking_completed(payload: Dict[str, Any]) -> None:
    """Handle booking.completed event from booking service."""
    db = SessionLocal()
    try:
        guest_id = UUID(payload.get("user_id"))
        booking_id = payload.get("booking_id")
        venue_id = payload.get("venue_id")
        
        interaction_type = InteractionService.get_interaction_type_by_name(
            db, "booking_completed"
        )
        if not interaction_type:
            logger.warning("Interaction type 'booking_completed' not found")
            return
        
        from app.schemas.interaction import InteractionCreate
        interaction_data = InteractionCreate(
            interaction_type_id=interaction_type.id,
            entity_type="booking",
            entity_id=booking_id,
            context={"venue_id": venue_id},
            source="booking_service",
            source_event_id=payload.get("event_id"),
        )
        
        InteractionService.create_interaction(db, guest_id, interaction_data)
        
        # Could also update preferences based on completed booking
        # (e.g., mark venue as preferred)
        logger.info(f"Recorded booking completion for guest {guest_id}")
    except Exception as e:
        logger.error(f"Error handling booking.completed event: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def handle_feedback_submitted(payload: Dict[str, Any]) -> None:
    """Handle feedback.review.submitted event from feedback service."""
    db = SessionLocal()
    try:
        guest_id = UUID(payload.get("user_id"))
        review_id = payload.get("review_id")
        venue_id = payload.get("venue_id")
        rating = payload.get("rating")
        
        interaction_type = InteractionService.get_interaction_type_by_name(
            db, "review_submitted"
        )
        if not interaction_type:
            logger.warning("Interaction type 'review_submitted' not found")
            return
        
        from app.schemas.interaction import InteractionCreate
        interaction_data = InteractionCreate(
            interaction_type_id=interaction_type.id,
            entity_type="review",
            entity_id=review_id,
            context={"venue_id": venue_id, "rating": rating},
            source="feedback_service",
            source_event_id=payload.get("event_id"),
        )
        
        InteractionService.create_interaction(db, guest_id, interaction_data)
        logger.info(f"Recorded review submission for guest {guest_id}")
    except Exception as e:
        logger.error(f"Error handling feedback.submitted event: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def handle_order_created(payload: Dict[str, Any]) -> None:
    """Handle order.created event from order service."""
    db = SessionLocal()
    try:
        guest_id = UUID(payload.get("user_id"))
        order_id = payload.get("order_id")
        venue_id = payload.get("venue_id")
        items = payload.get("items", [])
        
        interaction_type = InteractionService.get_interaction_type_by_name(
            db, "order_created"
        )
        if not interaction_type:
            logger.warning("Interaction type 'order_created' not found")
            return
        
        from app.schemas.interaction import InteractionCreate
        interaction_data = InteractionCreate(
            interaction_type_id=interaction_type.id,
            entity_type="order",
            entity_id=order_id,
            context={"venue_id": venue_id, "items": items},
            source="order_service",
            source_event_id=payload.get("event_id"),
        )
        
        InteractionService.create_interaction(db, guest_id, interaction_data)
        logger.info(f"Recorded order creation for guest {guest_id}")
    except Exception as e:
        logger.error(f"Error handling order.created event: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def handle_marketing_campaign_clicked(payload: Dict[str, Any]) -> None:
    """Handle marketing.campaign.clicked event from marketing service."""
    db = SessionLocal()
    try:
        guest_id = UUID(payload.get("user_id"))
        campaign_id = payload.get("campaign_id")
        
        interaction_type = InteractionService.get_interaction_type_by_name(
            db, "campaign_clicked"
        )
        if not interaction_type:
            logger.warning("Interaction type 'campaign_clicked' not found")
            return
        
        from app.schemas.interaction import InteractionCreate
        interaction_data = InteractionCreate(
            interaction_type_id=interaction_type.id,
            entity_type="campaign",
            entity_id=campaign_id,
            source="marketing_service",
            source_event_id=payload.get("event_id"),
        )
        
        InteractionService.create_interaction(db, guest_id, interaction_data)
        logger.info(f"Recorded campaign click for guest {guest_id}")
    except Exception as e:
        logger.error(f"Error handling marketing.campaign.clicked event: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def setup_event_handlers() -> None:
    """Register all event handlers."""
    # Booking service events
    event_consumer.register_handler(
        f"{settings.event_topic_booking}.created",
        handle_booking_created
    )
    event_consumer.register_handler(
        f"{settings.event_topic_booking}.completed",
        handle_booking_completed
    )
    
    # Feedback service events
    event_consumer.register_handler(
        f"{settings.event_topic_feedback}.review.submitted",
        handle_feedback_submitted
    )
    
    # Order service events
    event_consumer.register_handler(
        f"{settings.event_topic_order}.created",
        handle_order_created
    )
    
    # Marketing service events
    event_consumer.register_handler(
        f"{settings.event_topic_marketing}.campaign.clicked",
        handle_marketing_campaign_clicked
    )
    
    logger.info("Event handlers registered")
