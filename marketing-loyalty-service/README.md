# Marketing & Loyalty Service

Manages campaigns, promotions, loyalty programs, and targeted offers for the hospitality platform.

## Architecture

This service is designed as an **orchestration and decision layer**:

```
┌─────────────────────────────────────────────────────────────────┐
│                   Marketing & Loyalty Service                    │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Campaigns  │  │   Loyalty   │  │         Offers          │  │
│  │             │  │             │  │   (Frontend Exposure)   │  │
│  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘  │
│         │                │                      │                │
│         └────────────────┼──────────────────────┘                │
│                          │                                       │
│              ┌───────────▼───────────┐                          │
│              │   Eligibility Engine  │                          │
│              │   (Decision Layer)    │                          │
│              └───────────┬───────────┘                          │
└──────────────────────────┼──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │Personalization│ │  Sentiment  │ │  Analytics  │
    │   Service   │ │   Service   │ │   Service   │
    └─────────────┘ └─────────────┘ └─────────────┘
         (Consumes insights - does NOT generate them)
```

## Key Design Principles

1. **Consumes, doesn't generate insights**: Uses external services for personalization, sentiment analysis
2. **No pricing logic**: Returns offer codes/types; pricing service calculates discounts
3. **No booking rules**: Validates eligibility only; booking service enforces availability
4. **Event-driven**: Publishes engagement events for analytics and downstream processing

## API Endpoints

### Offers (Frontend-facing)
```
GET  /api/v1/offers/eligible/{guest_id}  # Get personalized offers
POST /api/v1/offers/claim                # Guest claims an offer
POST /api/v1/offers/redeem               # Redeem on booking
GET  /api/v1/offers/validate/{code}      # Validate for external services
```

### Campaigns
```
POST /api/v1/campaigns                   # Create campaign
GET  /api/v1/campaigns                   # List campaigns
GET  /api/v1/campaigns/active            # Get active campaigns
POST /api/v1/campaigns/{id}/activate     # Activate campaign
```

### Loyalty
```
GET  /api/v1/loyalty/member/{guest_id}         # Get member status
GET  /api/v1/loyalty/member/{guest_id}/history # Points history
POST /api/v1/loyalty/points/earn               # Award points
POST /api/v1/loyalty/points/redeem             # Redeem points
```

## Campaign Eligibility Rules

Eligibility is defined as JSON rules evaluated against guest insights:

```json
{
  "min_loyalty_tier": "gold",
  "sentiment_score_min": 0.6,
  "segments": ["frequent_guest", "business_traveler"]
}
```

## Events Published

| Event | Description |
|-------|-------------|
| `offer.presented` | Offer shown to guest |
| `offer.claimed` | Guest claimed offer |
| `offer.redeemed` | Offer applied to booking |
| `points.earned` | Loyalty points awarded |
| `tier.upgraded` | Member tier promotion |
| `campaign.created` | New campaign created |
| `campaign.activated` | Campaign went live |

## Running the Service

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (or use .env)
export DATABASE_URL=postgresql://user:pass@localhost:5432/marketing_loyalty_db

# Run
uvicorn app.main:app --host 0.0.0.0 --port 8008 --reload
```

## Integration Examples

### Frontend: Get offers for display
```javascript
const response = await fetch(`/api/v1/offers/eligible/${guestId}`);
const { offers, loyalty_tier, points_balance } = await response.json();
```

### Pricing Service: Validate offer before applying
```python
validation = requests.get(f"/api/v1/offers/validate/{offer_code}?guest_id={guest_id}")
if validation.json()["valid"]:
    # Apply discount based on offer_type and offer_value
    pass
```

### Booking Service: After booking completion
```python
# Award points
requests.post("/api/v1/loyalty/points/earn", json={
    "guest_id": guest_id,
    "points": booking_amount,  # 1 point per currency unit
    "description": f"Booking {booking_ref}",
    "source_type": "booking",
    "source_id": booking_id
})
```


