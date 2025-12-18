# Booking & Reservation Service

## Overview

The Booking & Reservation Service is a core transactional microservice responsible for managing the entire lifecycle of bookings and reservations across hotels, restaurants, cafes, and retail experiences. This service is the transactional core of the platform and ensures consistency, idempotency, and traceability.

## Service Responsibilities

### Core Responsibilities

1. **Booking Lifecycle Management**
   - Create, update, and cancel bookings
   - Manage booking status transitions (pending → confirmed → checked_in → completed)
   - Handle booking expiration and no-show scenarios
   - Maintain booking state as the single source of truth

2. **Availability Checking**
   - Check availability for booking slots
   - Coordinate with inventory service for capacity checks
   - Detect conflicts with existing bookings
   - Provide availability information to frontend

3. **External Service Coordination**
   - **Inventory Service**: Reserve and release inventory for bookings
   - **Pricing Service**: Get pricing information and estimates
   - **Payment Service**: Create payment intents and process refunds
   - Does NOT embed logic from these services - coordinates via HTTP

4. **Conflict Resolution**
   - Optimistic locking to prevent concurrent modification conflicts
   - Idempotency keys to prevent duplicate operations
   - Transaction isolation for consistency

5. **Event Emission**
   - Publishes booking lifecycle events for downstream consumers
   - Events consumed by analytics, personalization, housekeeping, and marketing services

### What This Service Does NOT Do

- **No Inventory Logic**: Does not own inventory management; coordinates with inventory service
- **No Pricing Logic**: Does not calculate prices; gets pricing from pricing service
- **No Payment Processing**: Does not process payments; coordinates with payment service
- **No AI/ML Logic**: Does not run recommendation or personalization algorithms

## Data Model Ownership

### Booking Entity

The service owns the `Booking` model which includes:
- Booking identification (ID, reference, idempotency key)
- Guest information (ID, name, email, phone)
- Venue information (ID, type, name)
- Booking details (date, time, duration, party size)
- Status and lifecycle tracking
- Pricing snapshot (at booking time)
- Payment coordination references
- Inventory coordination references
- Timestamps and audit trail

### Status History

All status transitions are recorded in `BookingStatusHistory` for full traceability.

### Idempotency Keys

Idempotency keys are stored to prevent duplicate operations and ensure idempotent API behavior.

## API Contracts

### Booking Management

- `POST /api/v1/bookings` - Create a new booking
- `GET /api/v1/bookings/{booking_id}` - Get booking by ID
- `GET /api/v1/bookings/reference/{booking_reference}` - Get booking by reference
- `PUT /api/v1/bookings/{booking_id}` - Update booking (requires version for optimistic locking)
- `POST /api/v1/bookings/{booking_id}/cancel` - Cancel booking
- `POST /api/v1/bookings/{booking_id}/status` - Update booking status

### Query Endpoints

- `GET /api/v1/bookings/guest/{guest_id}` - Get bookings for a guest
- `GET /api/v1/bookings/venue/{venue_id}` - Get bookings for a venue
- `POST /api/v1/bookings/availability/check` - Check availability

## Status Transitions

The service enforces a state machine for booking status:

```
PENDING → CONFIRMED → CHECKED_IN → COMPLETED
   ↓          ↓            ↓
CANCELLED  CANCELLED   CANCELLED
   ↓
EXPIRED
```

- **PENDING**: Created but not confirmed (expires after timeout)
- **CONFIRMED**: Confirmed and active
- **CHECKED_IN**: Guest has checked in
- **COMPLETED**: Booking completed successfully
- **CANCELLED**: Cancelled by guest or business
- **NO_SHOW**: Guest didn't show up
- **EXPIRED**: Booking expired without confirmation

## Conflict Handling

### Optimistic Locking

All update operations require an `expected_version` parameter. If the booking version doesn't match, the operation fails with a conflict error, requiring the client to refresh and retry.

### Idempotency

All create, update, and cancel operations support an optional `idempotency_key`. If the same key is used twice, the original result is returned without creating duplicates.

### Transaction Isolation

Database transactions ensure atomicity of booking operations and coordination with external services.

## External Service Coordination

### Inventory Service

- **Check Availability**: `POST /api/v1/inventory/check-availability`
- **Reserve Inventory**: `POST /api/v1/inventory/reserve`
- **Release Inventory**: `POST /api/v1/inventory/release`
- **Update Reservation**: `POST /api/v1/inventory/update-reservation`

### Pricing Service

- **Get Booking Price**: `POST /api/v1/pricing/calculate`
- **Estimate Price**: `POST /api/v1/pricing/estimate`

### Payment Service

- **Create Payment Intent**: `POST /api/v1/payments/intents`
- **Confirm Payment**: `POST /api/v1/payments/intents/{id}/confirm`
- **Get Payment Status**: `GET /api/v1/payments/intents/{id}`
- **Refund Payment**: `POST /api/v1/payments/refunds`

## Event Emission

The service emits events for downstream consumers:

- `booking.created` - New booking created
- `booking.updated` - Booking details updated
- `booking.cancelled` - Booking cancelled
- `booking.status_changed` - Status transition occurred
- `booking.confirmed` - Booking confirmed
- `booking.checked_in` - Guest checked in
- `booking.completed` - Booking completed
- `booking.expired` - Booking expired

Events are published to RabbitMQ/Kafka for consumption by:
- Analytics service (reporting and metrics)
- Personalization service (recommendations)
- Housekeeping service (operational tasks)
- Marketing service (campaigns and notifications)

## Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Event System**: Async event publishing (RabbitMQ/Kafka compatible)
- **HTTP Client**: httpx for external service coordination
- **Validation**: Pydantic models for request/response validation
- **Documentation**: OpenAPI/Swagger auto-generated

## Service Architecture

```
booking-reservation-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection and session management
│   ├── models/                 # SQLAlchemy database models
│   │   ├── __init__.py
│   │   └── booking.py          # Booking, BookingStatusHistory, IdempotencyKey models
│   ├── schemas/                # Pydantic schemas for API
│   │   ├── __init__.py
│   │   └── booking.py          # Request/response schemas
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── bookings.py     # Booking endpoints
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── booking_service.py  # Main booking orchestration
│   │   ├── availability_service.py  # Availability checking
│   │   └── conflict_resolution.py   # Conflict handling
│   ├── clients/                # External service clients
│   │   ├── __init__.py
│   │   ├── inventory_client.py     # Inventory service HTTP client
│   │   ├── pricing_client.py       # Pricing service HTTP client
│   │   └── payment_client.py       # Payment service HTTP client
│   ├── events/                 # Event publishing
│   │   ├── __init__.py
│   │   └── publisher.py        # Event publisher
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── booking_reference.py    # Reference generation
│       └── status_transitions.py   # Status transition validation
├── requirements.txt
├── README.md
└── ARCHITECTURE.md
```

## Setup

1. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (create `.env` file):
```env
DATABASE_URL=postgresql://booking_user:booking_password@localhost:5432/booking_reservation_db
INVENTORY_SERVICE_URL=http://localhost:8003
PRICING_SERVICE_URL=http://localhost:8004
PAYMENT_SERVICE_URL=http://localhost:8005
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

4. Run database migrations (using Alembic in production):
```bash
alembic upgrade head
```

5. Start the service:
```bash
uvicorn app.main:app --reload --port 8002
```

## Design Principles

### Correctness First

This service is designed for correctness, not AI intelligence:
- Strict state machine for status transitions
- Optimistic locking for conflict prevention
- Idempotency for duplicate prevention
- Transaction isolation for consistency
- Comprehensive error handling
- Full audit trail via status history

### Service Boundaries

- Owns booking state and lifecycle
- Coordinates with external services but doesn't embed their logic
- Emits events but doesn't consume booking events (avoids circular dependencies)
- Single responsibility: booking management

### Traceability

- All status changes recorded in history
- Idempotency keys tracked
- Version numbers for optimistic locking
- Timestamps for all lifecycle events
- Event emission for downstream consumers

## Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=app --cov-report=html
```

## API Documentation

Once the service is running, access:
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc


