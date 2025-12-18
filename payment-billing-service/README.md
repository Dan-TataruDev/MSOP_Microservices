# Payment & Billing Service

FastAPI microservice for payment processing, billing records, refunds, and invoicing.

## Overview

This service handles all payment and billing operations while remaining isolated from booking logic. It integrates with the booking service via events and maintains its own data ownership.

## Key Features

- **Payment Processing**: Abstracted payment provider integration (Stripe, PayPal, Square, etc.)
- **Payment Status Tracking**: Secure status exposure to frontend (no sensitive data)
- **Billing Records**: Audit trail for all financial transactions
- **Refunds**: Full and partial refund processing with retry logic
- **Invoicing**: Invoice generation and management
- **Event-Driven**: Consumes booking events, publishes payment events
- **Data Protection**: Sensitive data encrypted, never exposed to frontend

## Architecture

### Payment Provider Abstraction

The service uses an abstract `PaymentProviderClient` interface that:
- Hides provider-specific implementation details
- Sanitizes responses before exposing to frontend
- Stores raw provider responses securely (encrypted in production)
- Supports multiple providers (Stripe, PayPal, Square, etc.)

### Payment State Management

Payment states: `PENDING` → `PROCESSING` → `COMPLETED` / `FAILED`

- Payments are initiated via API
- Status can be polled or received via webhooks
- Automatic retry with exponential backoff on failures
- Status reconciliation with provider

### Event Integration

**Consumes:**
- `booking.created` - Can initiate payment if needed
- `booking.cancelled` - Auto-refund if enabled

**Publishes:**
- `payment.initiated` - Payment started
- `payment.completed` - Payment succeeded
- `payment.failed` - Payment failed
- `refund.initiated` - Refund started
- `refund.completed` - Refund succeeded

### Data Ownership

- **Payment Service owns**: Payment records, billing records, invoices, refunds
- **Booking Service owns**: Booking records, booking status
- **Coordination**: Via events and references (UUIDs), not foreign keys

### Failure Handling

- Retry logic with exponential backoff
- Idempotency keys for safe retries
- Failure reasons tracked
- Webhook reconciliation for status updates

## API Endpoints

### Payments
- `POST /api/v1/payments` - Create payment
- `GET /api/v1/payments/{payment_id}` - Get payment
- `GET /api/v1/payments/reference/{reference}` - Get payment status (safe for polling)
- `POST /api/v1/payments/{payment_id}/confirm` - Confirm payment
- `GET /api/v1/payments/booking/{booking_id}` - Get payments for booking

### Billing
- `GET /api/v1/billing/booking/{booking_id}` - Get billing records
- `GET /api/v1/billing/guest/{guest_id}` - Get guest billing records

### Invoices
- `POST /api/v1/invoices` - Create invoice
- `GET /api/v1/invoices/{invoice_id}` - Get invoice
- `GET /api/v1/invoices/number/{number}` - Get invoice by number
- `GET /api/v1/invoices/booking/{booking_id}` - Get invoices for booking
- `PATCH /api/v1/invoices/{invoice_id}` - Update invoice

### Refunds
- `POST /api/v1/refunds` - Create refund
- `GET /api/v1/refunds/{refund_id}` - Get refund
- `GET /api/v1/refunds/reference/{reference}` - Get refund by reference
- `GET /api/v1/refunds/payment/{payment_id}` - Get refunds for payment
- `POST /api/v1/refunds/{refund_id}/process` - Process refund

## Security

- **Sensitive Data**: Card numbers, provider secrets never exposed
- **Frontend Exposure**: Only last 4 digits, brand, status, amounts
- **Webhook Verification**: Signature verification for provider webhooks
- **Data Encryption**: Sensitive fields encrypted at rest (production)

## Configuration

Set environment variables or use `.env` file:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/payment_db
PAYMENT_PROVIDER=stripe
PAYMENT_PROVIDER_API_KEY=sk_...
PAYMENT_PROVIDER_SECRET_KEY=sk_...
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

## Running

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python -m app.main
# or
uvicorn app.main:app --reload
```

Service runs on `http://localhost:8005` by default.

## Database

Uses PostgreSQL. Tables are auto-created on startup (use Alembic migrations in production).

## Testing

```bash
pytest
```


