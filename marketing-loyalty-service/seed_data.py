"""
Seed script for marketing-loyalty-service.
Generates loyalty programs, members, campaigns, and offers.
"""
import sys
import os
from datetime import datetime, timedelta
import random
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.loyalty import LoyaltyProgram, LoyaltyMember, LoyaltyTier, PointsTransaction
from app.models.campaign import Campaign, CampaignStatus, CampaignType
from app.models.offer import Offer, OfferStatus, OfferType

Base.metadata.create_all(bind=engine)

GUEST_IDS = [str(uuid.uuid4()) for _ in range(500)]
VENUE_IDS = [str(uuid.uuid4()) for _ in range(10)]


def generate_loyalty_programs(db: Session, num_programs: int = 3):
    """Generate loyalty program records."""
    print(f"Generating {num_programs} loyalty programs...")
    
    programs = []
    program_names = ["Premium Rewards", "Elite Membership", "Standard Points"]
    
    for i in range(num_programs):
        program = LoyaltyProgram(
            name=program_names[i] if i < len(program_names) else f"Program {i+1}",
            description=f"Loyalty program {i+1} with tier-based rewards",
            base_earn_rate=random.uniform(0.5, 2.0),
            silver_threshold=random.randint(500, 2000),
            gold_threshold=random.randint(3000, 8000),
            platinum_threshold=random.randint(10000, 20000),
            silver_multiplier=random.uniform(1.1, 1.5),
            gold_multiplier=random.uniform(1.3, 2.0),
            platinum_multiplier=random.uniform(1.8, 3.0),
        )
        programs.append(program)
    
    db.bulk_save_objects(programs)
    db.commit()
    print(f"✓ Created {len(programs)} loyalty programs")
    return programs


def generate_loyalty_members(db: Session, programs: list, num_members: int = 400):
    """Generate loyalty member records."""
    print(f"Generating {num_members} loyalty members...")
    
    members = []
    for i in range(num_members):
        guest_id = random.choice(GUEST_IDS)
        program = random.choice(programs)
        
        points_balance = random.randint(0, 50000)
        lifetime_points = points_balance + random.randint(0, 100000)
        
        # Determine tier based on lifetime points
        if lifetime_points >= program.platinum_threshold:
            tier = LoyaltyTier.PLATINUM
        elif lifetime_points >= program.gold_threshold:
            tier = LoyaltyTier.GOLD
        elif lifetime_points >= program.silver_threshold:
            tier = LoyaltyTier.SILVER
        else:
            tier = LoyaltyTier.BRONZE
        
        member = LoyaltyMember(
            guest_id=uuid.UUID(guest_id),
            program_id=program.id,
            tier=tier,
            points_balance=points_balance,
            lifetime_points=lifetime_points,
            enrolled_at=datetime.utcnow() - timedelta(days=random.randint(0, 730)),
            tier_updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 180)),
        )
        members.append(member)
    
    db.bulk_save_objects(members)
    db.commit()
    print(f"✓ Created {len(members)} loyalty members")
    
    # Generate points transactions
    print("Generating points transactions...")
    transactions = []
    for member in members:
        # Earn transactions
        for _ in range(random.randint(5, 30)):
            points = random.randint(10, 500)
            transactions.append(PointsTransaction(
                member_id=member.id,
                points=points,
                description=random.choice([
                    "Points earned from booking",
                    "Bonus points from campaign",
                    "Referral bonus",
                    "Stay bonus",
                ]),
                source_type=random.choice(["booking", "campaign", "manual"]),
                source_id=uuid.uuid4(),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 180)),
            ))
            member.points_balance += points
        
        # Redeem transactions (for some members)
        if random.random() > 0.6:
            for _ in range(random.randint(1, 5)):
                points = -random.randint(100, 2000)
                if abs(points) <= member.points_balance:
                    transactions.append(PointsTransaction(
                        member_id=member.id,
                        points=points,
                        description=random.choice([
                            "Points redeemed for discount",
                            "Points redeemed for upgrade",
                            "Points redeemed for reward",
                        ]),
                        source_type="redemption",
                        source_id=uuid.uuid4(),
                        created_at=datetime.utcnow() - timedelta(days=random.randint(0, 90)),
                    ))
                    member.points_balance += points
    
    db.bulk_save_objects(transactions)
    db.commit()
    print(f"✓ Created {len(transactions)} points transactions")
    
    return members


def generate_campaigns(db: Session, num_campaigns: int = 50):
    """Generate campaign records."""
    print(f"Generating {num_campaigns} campaigns...")
    
    campaigns = []
    for i in range(num_campaigns):
        campaign_type = random.choice(list(CampaignType))
        status = random.choice(list(CampaignStatus))
        
        start_date = datetime.utcnow() - timedelta(days=random.randint(0, 180))
        end_date = start_date + timedelta(days=random.randint(7, 90))
        
        campaign = Campaign(
            campaign_code=f"CAMP{random.randint(10000, 99999)}",
            name=f"{campaign_type.value.title()} Campaign {i+1}",
            description=f"Marketing campaign for {campaign_type.value}",
            campaign_type=campaign_type,
            status=status,
            venue_id=uuid.UUID(random.choice(VENUE_IDS)) if random.random() > 0.3 else None,
            start_date=start_date,
            end_date=end_date,
            eligibility_rules={
                "min_loyalty_tier": random.choice(["bronze", "silver", "gold", "platinum"]) if random.random() > 0.5 else None,
                "min_booking_count": random.randint(1, 5) if random.random() > 0.7 else None,
            },
            campaign_config={
                "discount_type": "percentage" if random.random() > 0.5 else "fixed",
                "discount_value": random.randint(10, 30),
                "bonus_points": random.randint(100, 1000) if random.random() > 0.5 else None,
            },
            max_redemptions=random.randint(100, 10000) if random.random() > 0.5 else None,
            current_redemptions=random.randint(0, 1000) if status in [CampaignStatus.ACTIVE, CampaignStatus.COMPLETED] else 0,
            max_per_guest=random.randint(1, 3),
            priority=random.randint(0, 10),
            is_stackable=random.random() > 0.7,
        )
        campaigns.append(campaign)
    
    db.bulk_save_objects(campaigns)
    db.commit()
    print(f"✓ Created {len(campaigns)} campaigns")
    return campaigns


def generate_offers(db: Session, campaigns: list, num_offers: int = 800):
    """Generate offer records."""
    print(f"Generating {num_offers} offers...")
    
    offers = []
    for i in range(num_offers):
        guest_id = random.choice(GUEST_IDS)
        campaign = random.choice(campaigns) if random.random() > 0.3 else None
        
        offer_type = random.choice(list(OfferType))
        status = random.choice(list(OfferStatus))
        
        valid_from = datetime.utcnow() - timedelta(days=random.randint(0, 60))
        valid_until = valid_from + timedelta(days=random.randint(7, 30))
        
        presented_at = valid_from + timedelta(hours=random.randint(1, 24)) if status in [OfferStatus.PRESENTED, OfferStatus.CLAIMED, OfferStatus.REDEEMED] else None
        claimed_at = presented_at + timedelta(hours=random.randint(1, 48)) if status in [OfferStatus.CLAIMED, OfferStatus.REDEEMED] else None
        redeemed_at = claimed_at + timedelta(days=random.randint(1, 7)) if status == OfferStatus.REDEEMED else None
        
        offer = Offer(
            offer_code=f"OFFER{random.randint(100000, 999999)}",
            guest_id=uuid.UUID(guest_id),
            campaign_id=campaign.id if campaign else None,
            offer_type=offer_type,
            title=f"{offer_type.value.title()} Offer",
            description=f"Special {offer_type.value} offer for you",
            offer_value=random.choice(["SUMMER20", "WELCOME10", "LOYALTY500", "UPGRADE", "COMPLIMENTARY"]),
            valid_from=valid_from,
            valid_until=valid_until,
            status=status,
            presented_at=presented_at,
            claimed_at=claimed_at,
            redeemed_at=redeemed_at,
            redeemed_booking_id=uuid.uuid4() if status == OfferStatus.REDEEMED else None,
        )
        offers.append(offer)
    
    db.bulk_save_objects(offers)
    db.commit()
    print(f"✓ Created {len(offers)} offers")


def main():
    """Main function to seed the database."""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Seeding marketing-loyalty-service database...")
        print("=" * 60)
        
        programs = generate_loyalty_programs(db, num_programs=3)
        members = generate_loyalty_members(db, programs, num_members=400)
        campaigns = generate_campaigns(db, num_campaigns=50)
        generate_offers(db, campaigns, num_offers=800)
        
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

