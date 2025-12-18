# Guest Interaction & Personalization Service - Architecture

## Service Overview

The Guest Interaction & Personalization Service is a core microservice in the Smart Hospitality & Retail Platform. It serves as the single source of truth for guest identity, preferences, behavior signals, and personalization data.

## Core Responsibilities

### 1. Guest Identity Abstraction

The service maintains a unified view of guest identity independent of authentication systems:

- **Identity Mapping**: Maps multiple identity sources (session IDs, device IDs, auth user IDs, emails) to a single guest profile
- **Anonymous Guests**: Supports anonymous guest profiles that can be later linked to authenticated accounts
- **Identity Resolution**: Merges guest profiles when multiple identities are determined to belong to the same person
- **Cross-Platform Tracking**: Tracks guests across different devices and platforms

**Key Models:**
- `Guest`: Main guest profile entity
- `GuestIdentityMapping`: Maps external identities to guest IDs

### 2. Preference Storage & Management

Stores both explicit and implicit guest preferences:

- **Explicit Preferences**: Directly provided by guests (dietary restrictions, favorite categories, notification settings)
- **Implicit Preferences**: Derived from behavior (frequently viewed venues, preferred booking times)
- **Preference Versioning**: Tracks changes over time with full history
- **Confidence Scoring**: Assigns confidence scores to preferences based on source and evidence

**Key Models:**
- `Preference`: Individual preference with key-value structure
- `PreferenceCategory`: Categorizes preferences (dietary, notification, etc.)
- `PreferenceHistory`: Historical record of preference changes

**Preference Sources:**
- `explicit`: Directly set by the guest
- `implicit`: Inferred from behavior
- `inferred`: Derived by AI/ML systems
- `system`: System-generated defaults

### 3. Interaction History

Comprehensive tracking of all guest interactions:

- **View Events**: Venue views, product views, page views
- **Search Events**: Search queries, filters applied
- **Booking Events**: Booking creation, modification, cancellation, completion
- **Order Events**: Order placement, item selections
- **Feedback Events**: Review submissions, ratings
- **Marketing Events**: Campaign clicks, email opens, promotion usage

**Key Models:**
- `Interaction`: Individual interaction record
- `InteractionType`: Defines types of interactions

**Interaction Context:**
Each interaction stores:
- Entity type and ID (what was interacted with)
- Contextual data (search query, filters, etc.)
- Metadata (device info, session info)
- Source (which service/system recorded it)

### 4. Personalization Inputs

Provides structured data for AI-driven personalization:

- **Preference Vectors**: Structured representation of guest preferences
- **Behavior Summaries**: Aggregated behavior patterns
- **Guest Segments**: Behavioral and demographic segments
- **Behavior Signals**: Extracted signals from interactions

**Key Models:**
- `PersonalizationContext`: Aggregated context for AI services
- `GuestSegment`: Guest segmentation data
- `BehaviorSignal`: Extracted behavior signals

## API Design

### Frontend APIs (Direct Consumption)

The service exposes RESTful APIs for the frontend guest application:

#### Profile Management
```
GET    /api/v1/guests/{guest_id}/profile
GET    /api/v1/guests/me/profile
POST   /api/v1/guests
PATCH  /api/v1/guests/{guest_id}/profile
```

#### Preference Management
```
GET    /api/v1/guests/{guest_id}/preferences
GET    /api/v1/guests/{guest_id}/preferences/{key}
POST   /api/v1/guests/{guest_id}/preferences
PUT    /api/v1/guests/{guest_id}/preferences/{preference_id}
GET    /api/v1/guests/{guest_id}/preferences/history
GET    /api/v1/preference-categories
```

#### Interaction History
```
POST   /api/v1/guests/{guest_id}/interactions
GET    /api/v1/guests/{guest_id}/interactions
GET    /api/v1/interaction-types
```

#### Personalization Data
```
GET    /api/v1/guests/{guest_id}/personalization-context
GET    /api/v1/guests/{guest_id}/segments
GET    /api/v1/guests/{guest_id}/behavior-signals
POST   /api/v1/guests/{guest_id}/personalization-context/recompute
```

#### GDPR & Privacy
```
GET    /api/v1/guests/{guest_id}/data-export
DELETE /api/v1/guests/{guest_id}/data
GET    /api/v1/guests/{guest_id}/consent
PUT    /api/v1/guests/{guest_id}/consent
```

### Backend Service APIs (Indirect Consumption)

Other services consume personalization data through:

1. **Query APIs**: Direct queries for personalization context
   - `GET /api/v1/guests/{guest_id}/personalization-context` - Structured inputs for AI services
   - `GET /api/v1/guests/{guest_id}/segments` - Guest segments
   - `GET /api/v1/guests/{guest_id}/behavior-signals` - Behavior signals

2. **Event Subscriptions**: Services subscribe to events published by this service

## Event-Driven Architecture

### Events Published

This service publishes events when guest data changes:

#### Profile Events
- `guest.profile.created` - New guest profile created
- `guest.profile.updated` - Profile information updated
- `guest.profile.merged` - Multiple profiles merged

#### Preference Events
- `guest.preferences.updated` - Preferences changed
- `guest.preferences.category.added` - New preference category added
- `guest.preferences.category.removed` - Preference category removed

#### Interaction Events
- `guest.interaction.recorded` - New interaction logged
- `guest.interaction.batch.recorded` - Batch of interactions recorded

#### Privacy Events
- `guest.data.exported` - Data export requested (GDPR)
- `guest.data.deleted` - Data deletion requested (GDPR)
- `guest.consent.updated` - Consent preferences updated

### Events Consumed

This service consumes events from other services:

#### Booking Service
- `booking.created` → Records booking interaction
- `booking.cancelled` → Records cancellation interaction
- `booking.completed` → Records completion, may update preferences

#### Feedback Service
- `feedback.review.submitted` → Records review interaction, may update preferences
- `feedback.rating.submitted` → Records rating interaction

#### Order Service
- `order.created` → Records order interaction
- `order.items.selected` → Records item preferences

#### Marketing Service
- `marketing.campaign.clicked` → Records campaign interaction
- `marketing.email.opened` → Records email interaction
- `marketing.promotion.used` → Records promotion usage

## Data Ownership & Evolution

### Data Ownership

This service owns:
- Guest profile data (identity, contact info, status)
- Preference data (explicit and implicit)
- Interaction history (all guest interactions)
- Personalization data (segments, signals, context)

### Data Evolution

- **Versioning**: Preferences support versioning to track changes
- **Historical Data**: Interaction history maintained with configurable retention
- **Data Merging**: Supports merging guest data from multiple sources
- **Data Anonymization**: GDPR-compliant anonymization capabilities

### Data Retention

- Configurable retention period (default: 7 years)
- Automatic purging of expired data
- Anonymization option instead of deletion

## Privacy & GDPR Compliance

### Application-Level Privacy Features

1. **Data Minimization**
   - Only stores necessary guest data
   - Supports data retention policies
   - Automatic purging of expired data

2. **Consent Management**
   - Tracks consent for data processing
   - Supports granular consent categories:
     - Marketing communications
     - Analytics tracking
     - Personalization
   - Maintains consent history

3. **Right to Access (GDPR Article 15)**
   - `GET /api/v1/guests/{guest_id}/data-export`
   - Complete guest data retrieval in structured JSON format
   - Includes all preferences, interactions, segments, and signals

4. **Right to Erasure (GDPR Article 17)**
   - `DELETE /api/v1/guests/{guest_id}/data`
   - Complete data deletion with cascade
   - Anonymization option available

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

## Integration Patterns

### Frontend Integration

The frontend guest application integrates through:
- `@hospitality-platform/api-client` package
- `PersonalizationService` class
- Direct REST API calls for profile/preference management

### Backend Service Integration

Other services integrate through:
1. **Event Consumption**: Subscribe to guest-related events
2. **Query APIs**: Query personalization context when needed
3. **Event Publishing**: Publish events that this service consumes

### AI/ML Service Integration

AI-driven services consume:
- Personalization context (structured preference vectors, behavior summaries)
- Guest segments
- Behavior signals
- Historical interaction data

## Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Event System**: RabbitMQ/Kafka compatible (async event publishing/consuming)
- **Authentication**: JWT token validation (delegates to auth service)
- **Validation**: Pydantic models for request/response validation
- **Documentation**: OpenAPI/Swagger auto-generated

## Service Boundaries

### What This Service Does

✅ Manages guest profiles and identity
✅ Stores and manages preferences
✅ Tracks interaction history
✅ Provides personalization inputs
✅ Handles GDPR compliance
✅ Publishes guest-related events
✅ Consumes events from other services

### What This Service Does NOT Do

❌ Authentication/Authorization (delegates to auth service)
❌ Booking creation/modification (consumes booking events)
❌ Pricing calculations (no pricing logic)
❌ Payment processing (no payment logic)
❌ AI/ML model execution (provides inputs only)
❌ Recommendation generation (provides data to recommendation service)

## Scalability Considerations

- **Read-Heavy Workload**: Optimized for frequent reads of guest data
- **Event-Driven**: Asynchronous event processing for scalability
- **Database Indexing**: Comprehensive indexes on frequently queried fields
- **Caching**: Can be extended with Redis for frequently accessed data
- **Partitioning**: Interaction history can be partitioned by date for large datasets

## Security Considerations

- **Authentication**: All endpoints require JWT authentication (except health check)
- **Authorization**: Guest can only access their own data
- **Data Encryption**: Sensitive data encrypted at rest
- **Audit Logging**: All data access logged for compliance
- **Input Validation**: Pydantic schemas validate all inputs
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## Monitoring & Observability

- **Health Check**: `/health` endpoint for service health
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Event Tracking**: All events logged for debugging
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Metrics**: Can be extended with Prometheus metrics

## Future Enhancements

- Real-time WebSocket updates for preference changes
- Advanced preference inference from interactions
- Machine learning integration for segment assignment
- GraphQL API for flexible data querying
- Multi-tenant support for white-label deployments
