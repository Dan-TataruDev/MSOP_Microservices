# Guest Interaction & Personalization Service

## Overview

The Guest Interaction & Personalization Service is a core microservice responsible for managing guest profiles, preferences, behavior signals, and personalization data used across the Smart Hospitality & Retail Platform. This service serves as the single source of truth for guest identity abstraction, preference storage, interaction history, and personalization inputs.

## Service Responsibilities

### Core Responsibilities

1. **Guest Identity Abstraction**
   - Maintains unified guest profiles independent of authentication systems
   - Provides guest ID mapping and identity resolution
   - Supports anonymous-to-authenticated guest transitions
   - Manages guest identity across multiple touchpoints

2. **Preference Storage & Management**
   - Stores explicit preferences (dietary restrictions, favorite categories, notification settings)
   - Manages implicit preferences derived from behavior
   - Supports preference versioning and historical tracking
   - Provides preference inheritance and merging capabilities

3. **Interaction History**
   - Tracks guest interactions across the platform (views, searches, bookings, orders, feedback)
   - Maintains chronological interaction logs with timestamps
   - Stores interaction metadata and context
   - Supports interaction querying and analytics

4. **Personalization Inputs**
   - Aggregates structured data for AI-driven personalization services
   - Provides preference vectors and behavior signals
   - Exposes guest segments and characteristics
   - Supplies context for recommendation engines

### What This Service Does NOT Do

- **No Booking Logic**: Does not handle booking creation, modification, or cancellation
- **No Pricing Logic**: Does not calculate prices, discounts, or dynamic pricing
- **No Payment Logic**: Does not process payments or manage payment methods
- **No AI Processing**: Does not run AI models; provides structured inputs to AI services

## Data Ownership

### Guest Profile Data
- Guest identity information (ID, email, name, phone)
- Profile metadata (creation date, last updated, status)
- Identity resolution mappings (anonymous sessions, device IDs)

### Preference Data
- Explicit preferences (dietary, categories, notification settings)
- Implicit preferences (derived from behavior)
- Preference metadata (source, confidence, last updated)
- Preference history and versioning

### Interaction History
- View events (venue views, product views)
- Search events (queries, filters applied)
- Booking-related events (booking created, cancelled, completed)
- Order-related events (order placed, items selected)
- Feedback events (reviews submitted, ratings given)
- Marketing interaction events (campaign clicks, email opens)

### Personalization Data
- Guest segments and characteristics
- Behavior signals and patterns
- Preference vectors
- Personalization metadata (last computed, version)

### Data Evolution

- **Versioning**: Preferences and profiles support versioning to track changes over time
- **Historical Data**: Interaction history is maintained with retention policies
- **Data Merging**: Supports merging of guest data from multiple sources
- **Data Anonymization**: Supports GDPR-compliant data anonymization

## API Design

### Frontend APIs (Direct Consumption)

The service exposes REST APIs for the frontend guest application:

#### Profile Management
- `GET /api/v1/guests/{guest_id}/profile` - Get guest profile
- `PATCH /api/v1/guests/{guest_id}/profile` - Update guest profile
- `GET /api/v1/guests/me/profile` - Get current authenticated guest profile

#### Preference Management
- `GET /api/v1/guests/{guest_id}/preferences` - Get guest preferences
- `PUT /api/v1/guests/{guest_id}/preferences` - Update guest preferences
- `GET /api/v1/guests/{guest_id}/preferences/history` - Get preference change history

#### Interaction History
- `GET /api/v1/guests/{guest_id}/interactions` - Get interaction history with filtering
- `POST /api/v1/guests/{guest_id}/interactions` - Record a new interaction (frontend)

#### GDPR & Privacy
- `GET /api/v1/guests/{guest_id}/data-export` - Export all guest data (GDPR)
- `DELETE /api/v1/guests/{guest_id}/data` - Delete guest data (GDPR right to be forgotten)
- `GET /api/v1/guests/{guest_id}/consent` - Get consent status
- `PUT /api/v1/guests/{guest_id}/consent` - Update consent preferences

### Backend Service APIs (Indirect Consumption)

Other backend services consume personalization outputs indirectly through:

1. **Event Subscriptions**: Services subscribe to events published by this service
2. **Query APIs**: Services query guest data for personalization context
   - `GET /api/v1/guests/{guest_id}/personalization-context` - Get structured personalization inputs
   - `GET /api/v1/guests/{guest_id}/segments` - Get guest segments
   - `GET /api/v1/guests/{guest_id}/behavior-signals` - Get behavior signals

## Event-Driven Architecture

### Events Published

This service publishes events when guest data changes:

1. **Profile Events**
   - `guest.profile.created` - New guest profile created
   - `guest.profile.updated` - Profile information updated
   - `guest.profile.merged` - Multiple profiles merged

2. **Preference Events**
   - `guest.preferences.updated` - Preferences changed
   - `guest.preferences.category.added` - New preference category added
   - `guest.preferences.category.removed` - Preference category removed

3. **Interaction Events**
   - `guest.interaction.recorded` - New interaction logged
   - `guest.interaction.batch.recorded` - Batch of interactions recorded

4. **Privacy Events**
   - `guest.data.exported` - Data export requested (GDPR)
   - `guest.data.deleted` - Data deletion requested (GDPR)
   - `guest.consent.updated` - Consent preferences updated

### Events Consumed

This service consumes events from other services:

1. **Booking Service Events**
   - `booking.created` - Record booking interaction
   - `booking.cancelled` - Record cancellation interaction
   - `booking.completed` - Record completion, update preferences

2. **Feedback Service Events**
   - `feedback.review.submitted` - Record review interaction, update preferences
   - `feedback.rating.submitted` - Record rating interaction

3. **Marketing Service Events**
   - `marketing.campaign.clicked` - Record campaign interaction
   - `marketing.email.opened` - Record email interaction
   - `marketing.promotion.used` - Record promotion usage

4. **Order Service Events**
   - `order.created` - Record order interaction
   - `order.items.selected` - Record item preferences

## Privacy & GDPR Compliance

### Application-Level Privacy Features

1. **Data Minimization**
   - Only stores necessary guest data
   - Supports data retention policies
   - Automatic purging of expired data

2. **Consent Management**
   - Tracks consent for data processing
   - Supports granular consent categories
   - Maintains consent history

3. **Right to Access (GDPR Article 15)**
   - Data export functionality
   - Complete guest data retrieval in structured format

4. **Right to Erasure (GDPR Article 17)**
   - Complete data deletion
   - Anonymization options
   - Cascading deletion of related data

5. **Right to Rectification (GDPR Article 16)**
   - Profile update capabilities
   - Preference correction mechanisms

6. **Data Portability (GDPR Article 20)**
   - Structured data export (JSON)
   - Machine-readable format

7. **Privacy by Design**
   - Encryption at rest for sensitive data
   - Audit logging for data access
   - Access controls and authentication

## Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Event System**: Async event publishing/consuming (RabbitMQ/Kafka compatible)
- **Authentication**: JWT token validation (delegates to auth service)
- **Validation**: Pydantic models for request/response validation
- **Documentation**: OpenAPI/Swagger auto-generated

## Service Architecture

```
guest-interaction-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection and session management
│   ├── models/                 # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── guest.py            # Guest profile models
│   │   ├── preference.py       # Preference models
│   │   ├── interaction.py      # Interaction history models
│   │   └── personalization.py  # Personalization data models
│   ├── schemas/                # Pydantic schemas for API
│   │   ├── __init__.py
│   │   ├── guest.py
│   │   ├── preference.py
│   │   ├── interaction.py
│   │   └── personalization.py
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── guests.py       # Guest profile endpoints
│   │   │   ├── preferences.py  # Preference endpoints
│   │   │   ├── interactions.py # Interaction endpoints
│   │   │   └── privacy.py      # GDPR/privacy endpoints
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── guest_service.py
│   │   ├── preference_service.py
│   │   ├── interaction_service.py
│   │   └── personalization_service.py
│   ├── events/                 # Event handling
│   │   ├── __init__.py
│   │   ├── publisher.py        # Event publishing
│   │   ├── consumer.py         # Event consumption
│   │   └── handlers.py         # Event handlers
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── gdpr.py             # GDPR utilities
│       └── privacy.py          # Privacy helpers
├── tests/                      # Test suite
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- RabbitMQ or Kafka (for event streaming)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (see `.env.example`)

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the service:
```bash
uvicorn app.main:app --reload --port 8003
```

## API Documentation

Once the service is running, access interactive API documentation at:
- Swagger UI: `http://localhost:8003/docs`
- ReDoc: `http://localhost:8003/redoc`

## Integration with Frontend

The frontend guest application integrates with this service through the `@hospitality-platform/api-client` package. See the frontend integration section for details.

## Integration with Other Services

This service integrates with:
- **Auth Service**: Validates JWT tokens, receives user creation events
- **Booking Service**: Consumes booking events, publishes interaction events
- **Order Service**: Consumes order events, publishes interaction events
- **Feedback Service**: Consumes feedback events, publishes interaction events
- **Marketing Service**: Consumes marketing events, publishes interaction events
- **AI/Recommendation Service**: Provides personalization inputs via query APIs
