# Booking & Reservation Service - Architecture

## Service Overview

The Booking & Reservation Service is the transactional core of the Smart Hospitality & Retail Platform. It manages the entire lifecycle of bookings and reservations across hotels, restaurants, cafes, and retail experiences. The service is designed for correctness first, ensuring consistency, idempotency, and traceability.

## Core Responsibilities

### 1. Booking Lifecycle Management

The service owns the complete booking lifecycle from creation to completion:

**Booking Creation Process:**
1. Validate idempotency key (if provided)
2. Check availability (coordinate with inventory service)
3. Get pricing (coordinate with pricing service)
4. Reserve inventory (coordinate with inventory service)
5. Create booking record in database
6. Create payment intent (coordinate with payment service)
7. Record status history
8. Emit `booking.created` event

**Booking Update Process:**
1. Check optimistic lock (version matching)
2. Check idempotency key (if provided)
3. Recheck availability if time/party size changed
4. Update inventory reservation if needed
5. Get updated pricing if needed
6. Update booking record
7. Increment version for optimistic locking
8. Emit `booking.updated` event

**Booking Cancellation Process:**
1. Validate status can be cancelled
2. Check optimistic lock
3. Release inventory reservation
4. Process refund if payment was made
5. Update booking status to CANCELLED
6. Record cancellation details
7. Emit `booking.cancelled` event

**Status Transitions:**
- All status changes are validated against the state machine
- Status history is recorded for audit trail
- Events are emitted for downstream consumers

### 2. Availability Checking

The service checks availability by:
1. Querying existing bookings in the database for conflicts
2. Coordinating with inventory service for capacity checks
3. Getting price estimates from pricing service
4. Returning comprehensive availability information

**Conflict Detection:**
- Checks for overlapping time slots
- Considers booking duration
- Filters by active statuses (PENDING, CONFIRMED, CHECKED_IN)

### 3. External Service Coordination

The service coordinates with three external services without embedding their logic:

#### Inventory Service
- **Purpose**: Check capacity and reserve inventory
- **Coordination**: HTTP calls to inventory service API
- **Ownership**: Inventory service owns all inventory logic
- **Failure Handling**: If inventory service unavailable, booking creation fails (fail-safe)

#### Pricing Service
- **Purpose**: Get pricing information and estimates
- **Coordination**: HTTP calls to pricing service API
- **Ownership**: Pricing service owns all pricing logic
- **Failure Handling**: Falls back to default pricing if service unavailable (may need business decision)

#### Payment Service
- **Purpose**: Create payment intents and process refunds
- **Coordination**: HTTP calls to payment service API
- **Ownership**: Payment service owns all payment logic
- **Failure Handling**: If payment intent creation fails, booking creation is rolled back

### 4. Conflict Resolution

The service implements multiple conflict resolution strategies:

#### Optimistic Locking
- Each booking has a `version` field
- Update operations require `expected_version` parameter
- If version doesn't match, operation fails with conflict error
- Client must refresh and retry

#### Idempotency Keys
- Optional `idempotency_key` parameter for all operations
- Keys are stored with TTL (default 24 hours)
- Duplicate operations with same key return original result
- Prevents duplicate bookings from retries

#### Transaction Isolation
- Database transactions ensure atomicity
- External service calls are made within transactions
- Rollback on any failure ensures consistency

### 5. Event Emission

The service emits events for downstream consumers:

**Event Types:**
- `booking.created` - New booking created
- `booking.updated` - Booking details updated
- `booking.cancelled` - Booking cancelled
- `booking.status_changed` - Status transition occurred
- `booking.confirmed` - Booking confirmed
- `booking.checked_in` - Guest checked in
- `booking.completed` - Booking completed
- `booking.expired` - Booking expired

**Event Consumers:**
- **Analytics Service**: For reporting and metrics
- **Personalization Service**: For recommendation inputs
- **Housekeeping Service**: For operational task scheduling
- **Marketing Service**: For campaign triggers and notifications

## Data Model Ownership

### Booking Entity

The service owns the `Booking` model which is the single source of truth for booking state:

**Key Fields:**
- `id`: Primary key (UUID)
- `booking_reference`: Human-readable reference (e.g., BR-20241225-A3B9C2)
- `idempotency_key`: For duplicate prevention
- `guest_id`, `guest_name`, `guest_email`, `guest_phone`: Guest information
- `venue_id`, `venue_type`, `venue_name`: Venue information
- `booking_date`, `booking_time`, `duration_minutes`, `end_time`, `party_size`: Booking details
- `status`: Current status (enum)
- `version`: Optimistic locking version
- `base_price`, `tax_amount`, `discount_amount`, `total_price`, `currency`: Pricing snapshot
- `payment_intent_id`, `payment_status`: Payment coordination
- `inventory_reservation_id`, `inventory_item_id`: Inventory coordination
- `special_requests`, `internal_notes`: Additional information
- Timestamps: `created_at`, `updated_at`, `confirmed_at`, `cancelled_at`, `checked_in_at`, `completed_at`, `expires_at`
- `cancellation_reason`, `cancelled_by`: Cancellation details
- `source`, `metadata`: Additional metadata

**Indexes:**
- Primary key on `id`
- Unique index on `booking_reference`
- Indexes on `guest_id`, `venue_id`, `status`, `booking_date` for query performance
- Composite indexes for common query patterns

### BookingStatusHistory

Audit trail of all status transitions:
- `booking_id`: Foreign key to booking
- `from_status`, `to_status`: Status transition
- `changed_by`: Who made the change (guest_id, business_id, system)
- `reason`: Optional reason for change
- `created_at`: Timestamp of change

### IdempotencyKey

Tracks idempotency keys to prevent duplicate operations:
- `key`: The idempotency key
- `booking_id`: Associated booking (if operation completed)
- `operation_type`: create, update, cancel
- `request_hash`: Hash of request payload (for validation)
- `expires_at`: TTL for key cleanup

## API Contracts

### RESTful Endpoints

All endpoints follow RESTful conventions and return appropriate HTTP status codes.

**Booking Management:**
- `POST /api/v1/bookings` - Create booking (201 Created)
- `GET /api/v1/bookings/{id}` - Get booking (200 OK, 404 Not Found)
- `GET /api/v1/bookings/reference/{reference}` - Get by reference (200 OK, 404 Not Found)
- `PUT /api/v1/bookings/{id}` - Update booking (200 OK, 400 Bad Request, 404 Not Found, 409 Conflict)
- `POST /api/v1/bookings/{id}/cancel` - Cancel booking (200 OK, 400 Bad Request, 404 Not Found)
- `POST /api/v1/bookings/{id}/status` - Update status (200 OK, 400 Bad Request, 404 Not Found)

**Query Endpoints:**
- `GET /api/v1/bookings/guest/{guest_id}` - List guest bookings (200 OK)
- `GET /api/v1/bookings/venue/{venue_id}` - List venue bookings (200 OK)
- `POST /api/v1/bookings/availability/check` - Check availability (200 OK)

### Request/Response Formats

All requests and responses use JSON with Pydantic validation:
- Request bodies validated against Pydantic schemas
- Response models ensure consistent structure
- Error responses include detail messages

### Error Handling

**400 Bad Request:**
- Invalid request data
- Invalid status transition
- Business rule violations

**404 Not Found:**
- Booking not found

**409 Conflict:**
- Optimistic locking conflict (version mismatch)
- Idempotency key conflict

**500 Internal Server Error:**
- External service failures
- Database errors
- Unexpected errors

## Status State Machine

The service enforces a strict state machine for booking status:

```
                    ┌─────────┐
                    │ PENDING │
                    └────┬────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │CONFIRMED │    │CANCELLED │    │ EXPIRED  │
  └────┬─────┘    └──────────┘    └──────────┘
       │
       ▼
  ┌──────────┐
  │CHECKED_IN│
  └────┬─────┘
       │
       ├──────────┐
       │          │
       ▼          ▼
  ┌──────────┐ ┌──────────┐
  │COMPLETED │ │CANCELLED │
  └──────────┘ └──────────┘
```

**Valid Transitions:**
- PENDING → CONFIRMED, CANCELLED, EXPIRED
- CONFIRMED → CHECKED_IN, CANCELLED, COMPLETED
- CHECKED_IN → COMPLETED, CANCELLED
- Terminal states: COMPLETED, CANCELLED, NO_SHOW, EXPIRED

## Conflict Handling Strategies

### 1. Optimistic Locking

**Implementation:**
- Each booking has a `version` integer field
- Incremented on every update
- Client must provide `expected_version` in update requests
- If versions don't match, operation fails with 409 Conflict

**Benefits:**
- Prevents lost updates
- No locking overhead
- Works well for low contention

**Client Flow:**
1. GET booking (receive version)
2. Modify booking data
3. PUT booking with expected_version
4. If 409 Conflict, GET again and retry

### 2. Idempotency Keys

**Implementation:**
- Optional `idempotency_key` in create/update/cancel requests
- Keys stored in `IdempotencyKey` table with TTL
- If key exists and not expired, return original result
- Keys are operation-specific (create, update, cancel)

**Benefits:**
- Prevents duplicate operations from retries
- Safe for network failures
- Client can safely retry requests

**Usage:**
- Client generates unique key (UUID recommended)
- Include in request
- If request fails, retry with same key
- Service returns original result if key already processed

### 3. Transaction Isolation

**Implementation:**
- Database transactions wrap all operations
- External service calls within transactions
- Rollback on any failure

**Benefits:**
- Atomicity of operations
- Consistency guarantees
- No partial states

## External Service Coordination Patterns

### Request-Response Pattern

All coordination uses synchronous HTTP requests:
- FastAPI async/await for non-blocking I/O
- Configurable timeouts (default 5 seconds)
- Retry logic for transient failures
- Error handling with fallbacks where appropriate

### Failure Handling

**Inventory Service:**
- If unavailable, booking creation fails (fail-safe)
- Inventory must be available for booking

**Pricing Service:**
- If unavailable, falls back to default pricing
- May need business decision on fallback strategy

**Payment Service:**
- If payment intent creation fails, booking creation rolls back
- Payment is required for booking confirmation

### Service Discovery

In production, use service discovery (Consul, Eureka, Kubernetes services):
- Services identified by name
- Load balancing for multiple instances
- Health checks for availability

## Event-Driven Architecture

### Event Publishing

Events are published to message broker (RabbitMQ/Kafka):
- Async publishing (non-blocking)
- Event schema versioning
- Retry on publish failure
- Dead letter queue for failed events

### Event Schema

All events follow consistent schema:
```json
{
  "event_type": "booking.created",
  "payload": {
    "booking_id": "uuid",
    "booking_reference": "BR-20241225-A3B9C2",
    "guest_id": "uuid",
    "venue_id": "uuid",
    ...
  },
  "timestamp": "2024-12-25T10:00:00Z",
  "source": "booking-reservation-service",
  "version": "1.0"
}
```

### Event Consumers

Downstream services consume events asynchronously:
- **Analytics**: Aggregate booking metrics
- **Personalization**: Update guest preferences
- **Housekeeping**: Schedule operational tasks
- **Marketing**: Trigger campaigns

## Scalability Considerations

### Database

- Indexes on frequently queried fields
- Partitioning by date for large tables
- Read replicas for query scaling
- Connection pooling

### Caching

- Cache availability checks (short TTL)
- Cache booking lookups by reference
- Invalidate on updates

### Horizontal Scaling

- Stateless service design
- Database connection pooling
- External service load balancing
- Message broker for event distribution

## Security Considerations

### Authentication

- JWT token validation (delegates to auth service)
- Token in Authorization header
- Guest ID extracted from token

### Authorization

- Guests can only access their own bookings
- Businesses can access their venue bookings
- Admin access for all bookings

### Data Protection

- PII encryption at rest
- Audit logging for sensitive operations
- Rate limiting on endpoints
- Input validation and sanitization

## Monitoring and Observability

### Metrics

- Booking creation rate
- Booking cancellation rate
- Average booking value
- External service latency
- Error rates by endpoint

### Logging

- Structured logging (JSON)
- Request/response logging
- Error stack traces
- External service call logs

### Tracing

- Distributed tracing (OpenTelemetry)
- Trace IDs for request correlation
- Span tracking for external calls

## Testing Strategy

### Unit Tests

- Service layer logic
- Status transition validation
- Conflict resolution
- Utility functions

### Integration Tests

- Database operations
- External service coordination (mocked)
- API endpoint testing
- Event publishing

### End-to-End Tests

- Full booking lifecycle
- Failure scenarios
- Concurrent operations
- Idempotency verification

## Deployment

### Containerization

- Docker image with Python runtime
- Multi-stage builds for optimization
- Health check endpoints

### Orchestration

- Kubernetes deployment
- Horizontal pod autoscaling
- Service mesh for inter-service communication

### Database Migrations

- Alembic for schema migrations
- Version-controlled migrations
- Rollback capabilities

## Future Enhancements

1. **Saga Pattern**: For distributed transactions across services
2. **Event Sourcing**: For complete audit trail
3. **CQRS**: Separate read/write models for scaling
4. **Booking Templates**: For recurring bookings
5. **Waitlist Management**: For fully booked venues
6. **Dynamic Pricing Integration**: Real-time pricing updates


