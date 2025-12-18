"""
Offer service - generates and manages personalized offers.

This is the primary orchestration layer for exposing offers to frontend:
- Evaluates campaign eligibility
- Generates personalized offers
- Tracks offer lifecycle (presented → claimed → redeemed)
- Does NOT calculate final prices or validate bookings
"""
import logging
import uuid
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.campaign import Campaign, CampaignStatus
from app.models.offer import Offer, OfferStatus, OfferType
from app.models.loyalty import LoyaltyMember
from app.services.campaign_service import CampaignService
from app.events.publisher import event_publisher

logger = logging.getLogger(__name__)


def generate_offer_code() -> str:
    """Generate unique offer code."""
    return f"OFR-{uuid.uuid4().hex[:10].upper()}"


class OfferService:
    """
    Offer management service.
    
    Orchestrates offer generation and lifecycle without
    embedding pricing or booking logic.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.campaign_service = CampaignService(db)
    
    def get_eligible_offers(self, guest_id: uuid.UUID, guest_insights: dict, loyalty_member: LoyaltyMember = None) -> List[Offer]:
        """
        Get all offers a guest is eligible for.
        
        This is the main entry point for frontend to fetch personalized offers.
        Evaluates active campaigns and returns/creates personalized offers.
        """
        # Get existing pending/presented offers
        existing = self.db.query(Offer).filter(
            Offer.guest_id == guest_id,
            Offer.status.in_([OfferStatus.PENDING, OfferStatus.PRESENTED]),
            Offer.valid_until >= datetime.utcnow(),
        ).all()
        
        existing_campaign_ids = {o.campaign_id for o in existing if o.campaign_id}
        
        # Get active campaigns
        campaigns = self.campaign_service.get_active_campaigns()
        loyalty_tier = loyalty_member.tier.value if loyalty_member else None
        
        # Generate new offers for eligible campaigns
        new_offers = []
        for campaign in campaigns:
            if campaign.id in existing_campaign_ids:
                continue
            
            if self.campaign_service.check_eligibility(campaign, guest_insights, loyalty_tier):
                offer = self._create_offer_from_campaign(guest_id, campaign)
                if offer:
                    new_offers.append(offer)
        
        return existing + new_offers
    
    def _create_offer_from_campaign(self, guest_id: uuid.UUID, campaign: Campaign) -> Optional[Offer]:
        """Create a personalized offer from a campaign."""
        # Check max per guest
        existing_count = self.db.query(Offer).filter(
            Offer.guest_id == guest_id,
            Offer.campaign_id == campaign.id,
        ).count()
        
        if existing_count >= campaign.max_per_guest:
            return None
        
        config = campaign.campaign_config
        offer_type = self._map_campaign_to_offer_type(campaign.campaign_type, config)
        
        offer = Offer(
            offer_code=generate_offer_code(),
            guest_id=guest_id,
            campaign_id=campaign.id,
            offer_type=offer_type,
            title=campaign.name,
            description=campaign.description,
            offer_value=config.get("discount_code") or config.get("bonus_points") or str(config.get("value", "")),
            valid_from=datetime.utcnow(),
            valid_until=min(campaign.end_date, datetime.utcnow() + timedelta(days=30)),
        )
        
        self.db.add(offer)
        self.db.commit()
        self.db.refresh(offer)
        
        logger.info(f"Offer created: {offer.offer_code} for guest {guest_id}")
        return offer
    
    def _map_campaign_to_offer_type(self, campaign_type, config: dict) -> OfferType:
        """Map campaign type to offer type."""
        if "bonus_points" in config:
            return OfferType.BONUS_POINTS
        if config.get("is_upgrade"):
            return OfferType.UPGRADE
        return OfferType.DISCOUNT
    
    def mark_presented(self, offer_id: uuid.UUID) -> Optional[Offer]:
        """Mark offer as presented to guest."""
        offer = self.db.query(Offer).filter(Offer.id == offer_id).first()
        if offer and offer.status == OfferStatus.PENDING:
            offer.status = OfferStatus.PRESENTED
            offer.presented_at = datetime.utcnow()
            self.db.commit()
            event_publisher.publish_offer_presented(offer.id, offer.guest_id, offer.campaign_id)
        return offer
    
    def claim_offer(self, offer_code: str, guest_id: uuid.UUID) -> Optional[Offer]:
        """Guest claims an offer."""
        offer = self.db.query(Offer).filter(
            Offer.offer_code == offer_code,
            Offer.guest_id == guest_id,
        ).first()
        
        if not offer or offer.status not in [OfferStatus.PENDING, OfferStatus.PRESENTED]:
            return None
        
        if offer.valid_until < datetime.utcnow():
            offer.status = OfferStatus.EXPIRED
            self.db.commit()
            return None
        
        offer.status = OfferStatus.CLAIMED
        offer.claimed_at = datetime.utcnow()
        self.db.commit()
        
        event_publisher.publish_offer_claimed(offer.id, offer.guest_id, offer.campaign_id)
        return offer
    
    def redeem_offer(self, offer_code: str, guest_id: uuid.UUID, booking_id: uuid.UUID) -> Optional[Offer]:
        """
        Redeem an offer on a booking.
        
        Note: This records the redemption but does NOT calculate
        the discount. The booking/pricing service will call back
        to validate and apply the actual discount.
        """
        offer = self.db.query(Offer).filter(
            Offer.offer_code == offer_code,
            Offer.guest_id == guest_id,
            Offer.status == OfferStatus.CLAIMED,
        ).first()
        
        if not offer:
            return None
        
        offer.status = OfferStatus.REDEEMED
        offer.redeemed_at = datetime.utcnow()
        offer.redeemed_booking_id = booking_id
        
        # Increment campaign redemption
        if offer.campaign_id:
            self.campaign_service.increment_redemption(offer.campaign_id)
        
        self.db.commit()
        
        event_publisher.publish_offer_redeemed(offer.id, offer.guest_id, booking_id)
        return offer
    
    def get_offer_by_code(self, offer_code: str) -> Optional[Offer]:
        """Get offer by code."""
        return self.db.query(Offer).filter(Offer.offer_code == offer_code).first()
    
    def validate_offer(self, offer_code: str, guest_id: uuid.UUID) -> dict:
        """
        Validate an offer for use.
        
        Returns validation result for external services (pricing, booking)
        to use when applying discounts.
        """
        offer = self.get_offer_by_code(offer_code)
        
        if not offer:
            return {"valid": False, "reason": "Offer not found"}
        if offer.guest_id != guest_id:
            return {"valid": False, "reason": "Offer not for this guest"}
        if offer.status == OfferStatus.REDEEMED:
            return {"valid": False, "reason": "Offer already redeemed"}
        if offer.status == OfferStatus.EXPIRED or offer.valid_until < datetime.utcnow():
            return {"valid": False, "reason": "Offer expired"}
        
        return {
            "valid": True,
            "offer_type": offer.offer_type.value,
            "offer_value": offer.offer_value,
            "campaign_id": str(offer.campaign_id) if offer.campaign_id else None,
        }


