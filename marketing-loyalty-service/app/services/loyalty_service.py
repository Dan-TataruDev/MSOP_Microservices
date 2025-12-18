"""
Loyalty service - manages loyalty programs and member points.

Orchestration layer for loyalty:
- Tracks points and tiers
- Does NOT calculate pricing discounts (that's pricing service)
- Does NOT validate bookings (that's booking service)
"""
import logging
import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.loyalty import LoyaltyProgram, LoyaltyMember, LoyaltyTier, PointsTransaction as PointsTransactionModel
from app.events.publisher import event_publisher

logger = logging.getLogger(__name__)


class LoyaltyService:
    """
    Loyalty program management service.
    
    Manages member status and points, publishes events for
    downstream processing.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_member(self, guest_id: uuid.UUID, program_id: uuid.UUID = None) -> LoyaltyMember:
        """Get existing member or create new enrollment."""
        member = self.db.query(LoyaltyMember).filter(LoyaltyMember.guest_id == guest_id).first()
        if member:
            return member
        
        # Auto-enroll in default program
        if not program_id:
            program = self.db.query(LoyaltyProgram).first()
            if not program:
                program = LoyaltyProgram(name="Default Rewards")
                self.db.add(program)
                self.db.commit()
            program_id = program.id
        
        member = LoyaltyMember(guest_id=guest_id, program_id=program_id)
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        
        logger.info(f"New loyalty member enrolled: {guest_id}")
        return member
    
    def get_member(self, guest_id: uuid.UUID) -> Optional[LoyaltyMember]:
        """Get member by guest ID."""
        return self.db.query(LoyaltyMember).filter(LoyaltyMember.guest_id == guest_id).first()
    
    def earn_points(self, guest_id: uuid.UUID, points: int, description: str, source_type: str, source_id: uuid.UUID = None) -> LoyaltyMember:
        """
        Award points to a member.
        
        Points calculation happens here, but the source amount/reason
        comes from external events (booking completed, campaign bonus, etc.)
        """
        member = self.get_or_create_member(guest_id)
        
        # Apply tier multiplier
        program = self.db.query(LoyaltyProgram).filter(LoyaltyProgram.id == member.program_id).first()
        multiplier = self._get_tier_multiplier(member.tier, program)
        actual_points = int(points * multiplier)
        
        # Record transaction
        transaction = PointsTransactionModel(
            member_id=member.id,
            points=actual_points,
            description=description,
            source_type=source_type,
            source_id=source_id,
        )
        self.db.add(transaction)
        
        # Update balance
        member.points_balance += actual_points
        member.lifetime_points += actual_points
        
        # Check tier upgrade
        old_tier = member.tier
        self._update_tier(member, program)
        
        self.db.commit()
        
        event_publisher.publish_points_earned(guest_id, actual_points, source_type)
        if member.tier != old_tier:
            event_publisher.publish_tier_upgraded(guest_id, old_tier.value, member.tier.value)
        
        return member
    
    def redeem_points(self, guest_id: uuid.UUID, points: int, description: str, source_type: str = "redemption", source_id: uuid.UUID = None) -> Optional[LoyaltyMember]:
        """Redeem points from a member's balance."""
        member = self.get_member(guest_id)
        if not member or member.points_balance < points:
            return None
        
        transaction = PointsTransactionModel(
            member_id=member.id,
            points=-points,
            description=description,
            source_type=source_type,
            source_id=source_id,
        )
        self.db.add(transaction)
        member.points_balance -= points
        self.db.commit()
        
        return member
    
    def get_points_history(self, guest_id: uuid.UUID, limit: int = 20) -> List[PointsTransactionModel]:
        """Get points transaction history."""
        member = self.get_member(guest_id)
        if not member:
            return []
        
        return (
            self.db.query(PointsTransactionModel)
            .filter(PointsTransactionModel.member_id == member.id)
            .order_by(PointsTransactionModel.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def _get_tier_multiplier(self, tier: LoyaltyTier, program: LoyaltyProgram) -> float:
        """Get earning multiplier for tier."""
        if not program:
            return 1.0
        return {
            LoyaltyTier.BRONZE: 1.0,
            LoyaltyTier.SILVER: program.silver_multiplier,
            LoyaltyTier.GOLD: program.gold_multiplier,
            LoyaltyTier.PLATINUM: program.platinum_multiplier,
        }.get(tier, 1.0)
    
    def _update_tier(self, member: LoyaltyMember, program: LoyaltyProgram) -> None:
        """Update member tier based on lifetime points."""
        if not program:
            return
        
        old_tier = member.tier
        if member.lifetime_points >= program.platinum_threshold:
            member.tier = LoyaltyTier.PLATINUM
        elif member.lifetime_points >= program.gold_threshold:
            member.tier = LoyaltyTier.GOLD
        elif member.lifetime_points >= program.silver_threshold:
            member.tier = LoyaltyTier.SILVER
        
        if member.tier != old_tier:
            member.tier_updated_at = datetime.utcnow()


