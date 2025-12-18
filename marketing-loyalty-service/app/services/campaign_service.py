"""
Campaign service - orchestrates campaign management and eligibility.

This service acts as an orchestration layer:
- Defines and manages campaigns
- Evaluates eligibility using external insights
- Does NOT calculate pricing (delegates to pricing service)
- Does NOT enforce booking rules (delegates to booking service)
"""
import logging
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.campaign import Campaign, CampaignStatus, CampaignType
from app.schemas.campaign import CampaignCreate, CampaignUpdate
from app.events.publisher import event_publisher

logger = logging.getLogger(__name__)


def generate_campaign_code() -> str:
    """Generate unique campaign code."""
    return f"CMP-{uuid.uuid4().hex[:8].upper()}"


class CampaignService:
    """
    Campaign management service.
    
    Design: This service orchestrates campaign logic without
    embedding pricing or booking rules.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_campaign(self, data: CampaignCreate, created_by: uuid.UUID = None) -> Campaign:
        """Create a new campaign."""
        campaign = Campaign(
            campaign_code=generate_campaign_code(),
            name=data.name,
            description=data.description,
            campaign_type=data.campaign_type,
            venue_id=data.venue_id,
            start_date=data.start_date,
            end_date=data.end_date,
            eligibility_rules=data.eligibility_rules,
            campaign_config=data.campaign_config,
            max_redemptions=data.max_redemptions,
            max_per_guest=data.max_per_guest,
            priority=data.priority,
            is_stackable=data.is_stackable,
            created_by=created_by,
        )
        
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        
        event_publisher.publish_campaign_created(campaign.id, {"name": campaign.name, "type": campaign.campaign_type.value})
        logger.info(f"Campaign created: {campaign.campaign_code}")
        return campaign
    
    def get_campaign(self, campaign_id: uuid.UUID) -> Optional[Campaign]:
        """Get campaign by ID."""
        return self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    def get_active_campaigns(self, venue_id: uuid.UUID = None) -> List[Campaign]:
        """Get all currently active campaigns."""
        now = datetime.utcnow()
        query = self.db.query(Campaign).filter(
            and_(
                Campaign.status == CampaignStatus.ACTIVE,
                Campaign.start_date <= now,
                Campaign.end_date >= now,
            )
        )
        if venue_id:
            query = query.filter((Campaign.venue_id == venue_id) | (Campaign.venue_id.is_(None)))
        
        return query.order_by(Campaign.priority.desc()).all()
    
    def activate_campaign(self, campaign_id: uuid.UUID) -> Optional[Campaign]:
        """Activate a campaign."""
        campaign = self.get_campaign(campaign_id)
        if campaign and campaign.status == CampaignStatus.DRAFT:
            campaign.status = CampaignStatus.SCHEDULED if campaign.start_date > datetime.utcnow() else CampaignStatus.ACTIVE
            self.db.commit()
            if campaign.status == CampaignStatus.ACTIVE:
                event_publisher.publish_campaign_activated(campaign.id)
        return campaign
    
    def check_eligibility(self, campaign: Campaign, guest_insights: Dict[str, Any], loyalty_tier: str = None) -> bool:
        """
        Check if a guest is eligible for a campaign.
        
        Uses insights from external services (consumed, not generated).
        Does NOT check pricing or booking availability.
        """
        rules = campaign.eligibility_rules
        if not rules:
            return True
        
        # Check loyalty tier requirement
        if "min_loyalty_tier" in rules:
            tier_order = {"bronze": 0, "silver": 1, "gold": 2, "platinum": 3}
            required_tier = tier_order.get(rules["min_loyalty_tier"], 0)
            guest_tier = tier_order.get(loyalty_tier, 0) if loyalty_tier else 0
            if guest_tier < required_tier:
                return False
        
        # Check sentiment score requirement
        if "sentiment_score_min" in rules:
            guest_score = guest_insights.get("sentiment_score")
            if guest_score is None or guest_score < rules["sentiment_score_min"]:
                return False
        
        # Check segment requirement
        if "segments" in rules:
            guest_segments = guest_insights.get("segments", [])
            if not any(seg in guest_segments for seg in rules["segments"]):
                return False
        
        return True
    
    def increment_redemption(self, campaign_id: uuid.UUID) -> None:
        """Increment campaign redemption count."""
        campaign = self.get_campaign(campaign_id)
        if campaign:
            campaign.current_redemptions += 1
            if campaign.max_redemptions and campaign.current_redemptions >= campaign.max_redemptions:
                campaign.status = CampaignStatus.COMPLETED
            self.db.commit()
    
    def list_campaigns(self, status: CampaignStatus = None, page: int = 1, page_size: int = 20) -> tuple[List[Campaign], int]:
        """List campaigns with pagination."""
        query = self.db.query(Campaign)
        if status:
            query = query.filter(Campaign.status == status)
        
        total = query.count()
        items = query.order_by(Campaign.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total


