# Quick Start Guide

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 14 or higher
- RabbitMQ (optional, for event streaming in production)

## Setup

### 1. Install Dependencies

```bash
cd guest-interaction-service
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
- Database connection string
- RabbitMQ connection (if using)
- JWT secret key
- Other service URLs

### 3. Set Up Database

Create the PostgreSQL database:

```sql
CREATE DATABASE guest_interaction_db;
```

Run migrations (if using Alembic):

```bash
alembic upgrade head
```

Or create tables directly (for development):

```bash
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 4. Initialize Seed Data (Optional)

Create initial interaction types and preference categories:

```python
# scripts/seed_data.py
from app.database import SessionLocal
from app.models.interaction import InteractionType
from app.models.preference import PreferenceCategory

db = SessionLocal()

# Create interaction types
interaction_types = [
    {"name": "venue_viewed", "category": "view", "description": "Guest viewed a venue"},
    {"name": "product_viewed", "category": "view", "description": "Guest viewed a product"},
    {"name": "search_performed", "category": "search", "description": "Guest performed a search"},
    {"name": "booking_created", "category": "booking", "description": "Guest created a booking"},
    {"name": "booking_completed", "category": "booking", "description": "Guest completed a booking"},
    {"name": "order_created", "category": "order", "description": "Guest created an order"},
    {"name": "review_submitted", "category": "feedback", "description": "Guest submitted a review"},
    {"name": "campaign_clicked", "category": "marketing", "description": "Guest clicked a campaign"},
]

for it_data in interaction_types:
    it = InteractionType(**it_data)
    db.add(it)

# Create preference categories
preference_categories = [
    {"name": "dietary", "description": "Dietary restrictions and preferences", "is_system": True},
    {"name": "notification", "description": "Notification preferences", "is_system": True},
    {"name": "category", "description": "Favorite categories", "is_system": True},
    {"name": "cuisine", "description": "Cuisine preferences", "is_system": True},
]

for pc_data in preference_categories:
    pc = PreferenceCategory(**pc_data)
    db.add(pc)

db.commit()
db.close()
```

### 5. Start the Service

```bash
uvicorn app.main:app --reload --port 8003
```

Or use the Python script:

```bash
python -m app.main
```

The service will be available at:
- API: `http://localhost:8003`
- Swagger UI: `http://localhost:8003/docs`
- ReDoc: `http://localhost:8003/redoc`

## Testing the API

### 1. Create a Guest Profile

```bash
curl -X POST "http://localhost:8003/api/v1/guests" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "guest@example.com",
    "name": "John Doe",
    "consent_marketing": true,
    "consent_analytics": true,
    "consent_personalization": true
  }'
```

### 2. Get Guest Profile

```bash
curl "http://localhost:8003/api/v1/guests/{guest_id}/profile"
```

### 3. Create a Preference

```bash
curl -X POST "http://localhost:8003/api/v1/guests/{guest_id}/preferences" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": "{category_id}",
    "key": "dietary_restrictions",
    "value": ["vegetarian", "gluten-free"],
    "value_type": "array",
    "source": "explicit"
  }'
```

### 4. Record an Interaction

```bash
curl -X POST "http://localhost:8003/api/v1/guests/{guest_id}/interactions" \
  -H "Content-Type: application/json" \
  -d '{
    "interaction_type_id": "{interaction_type_id}",
    "entity_type": "venue",
    "entity_id": "venue_123",
    "context": {"search_query": "italian restaurant"},
    "source": "frontend"
  }'
```

### 5. Get Personalization Context

```bash
curl "http://localhost:8003/api/v1/guests/{guest_id}/personalization-context"
```

### 6. Export Guest Data (GDPR)

```bash
curl "http://localhost:8003/api/v1/guests/{guest_id}/data-export"
```

## Frontend Integration

The frontend is already configured to use this service through the `@hospitality-platform/api-client` package.

### Example Usage in Frontend

```typescript
import { createApiServices } from '@hospitality-platform/api-client';
import { tokenStorage } from './storage';

const api = createApiServices(tokenStorage);

// Get guest profile
const profile = await api.personalization.getCurrentGuestProfile();

// Get preferences
const preferences = await api.personalization.getGuestPreferences(profile.data.id);

// Create preference
await api.personalization.createPreference(profile.data.id, {
  categoryId: 'dietary-category-id',
  key: 'dietary_restrictions',
  value: ['vegetarian'],
  valueType: 'array',
});

// Record interaction
await api.personalization.createInteraction(profile.data.id, {
  interactionTypeId: 'interaction-type-id',
  entityType: 'venue',
  entityId: 'venue-123',
  source: 'frontend',
});
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
isort app/
```

### Type Checking

```bash
mypy app/
```

## Production Deployment

1. Set `ENVIRONMENT=production` and `DEBUG=false` in `.env`
2. Use a production-grade database (PostgreSQL with proper configuration)
3. Set up RabbitMQ or Kafka for event streaming
4. Configure proper authentication middleware
5. Set up monitoring and logging
6. Use a process manager like systemd or supervisor
7. Set up reverse proxy (nginx) with SSL

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

### Event Publishing Not Working

- Event publishing is currently logged only (not connected to message broker)
- In production, configure RabbitMQ/Kafka connection
- Check `RABBITMQ_URL` in `.env`

### Import Errors

- Ensure you're in the correct directory
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.11+)

## Next Steps

- Review [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture
- Review [README.md](./README.md) for service overview
- Set up event streaming for production
- Configure authentication middleware
- Set up monitoring and alerting
