# Housekeeping & Maintenance Service

A FastAPI microservice for managing operational tasks including cleaning schedules, maintenance requests, and task completion tracking in a hospitality platform.

## Architecture Overview

This service follows an **event-driven architecture** to maintain loose coupling with other microservices:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Housekeeping & Maintenance Service                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                 │
│   │    Tasks     │    │  Schedules   │    │ Maintenance  │                 │
│   │   Service    │    │   Service    │    │   Service    │                 │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                 │
│          │                   │                   │                          │
│          └───────────────────┼───────────────────┘                          │
│                              │                                              │
│                    ┌─────────▼─────────┐                                   │
│                    │   Dashboard       │                                   │
│                    │   Service         │                                   │
│                    └───────────────────┘                                   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                         Event Layer (RabbitMQ)                              │
├──────────────────────┬──────────────────────────────────────────────────────┤
│   Events Consumed    │   Events Published                                   │
│   ─────────────────  │   ─────────────────                                  │
│   • booking.completed│   • task.created                                     │
│   • booking.cancelled│   • task.completed                                   │
│   • inventory.low    │   • task.delayed                                     │
│   • guest.complaint  │   • room.ready                                       │
│                      │   • maintenance.resolved                             │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

## Key Design Principles

### 1. Event-Driven Task Generation
Tasks are automatically created in response to events from other services:
- **Booking checkout** → Checkout cleaning task
- **Low stock alert** → Restocking task
- **Guest complaint** → Maintenance request

### 2. No Direct Database Coupling
This service maintains its own database and stores only **reference IDs** from other services:
- `venue_id` - Reference to room/table in Inventory Service
- `booking_reference` - Reference to booking in Booking Service
- `guest_id` - Reference to guest profile

### 3. Event Publishing for Coordination
Key state changes are published as events for downstream consumers:
- `room.ready` - Consumed by Booking Service to update availability
- `task.delayed` - Consumed by Notification Service for alerts
- `maintenance.resolved` - Consumed by Inventory Service to update room status

## Features

### Task Management
- Create, assign, and track operational tasks
- Automatic priority calculation
- SLA tracking and delay detection
- Workload-balanced auto-assignment

### Cleaning Schedules
- Define recurring cleaning patterns
- Time-based triggers (daily, weekly, monthly)
- Event-based triggers (on checkout, on checkin)
- Automatic task generation

### Maintenance Requests
- Full lifecycle tracking (report → triage → resolve)
- Priority-based SLA calculation
- Safety concern flagging
- Parts and cost tracking

### Operational Dashboards
- Real-time status monitoring
- Task and maintenance metrics
- Staff workload visualization
- Daily/weekly/monthly reports

## API Endpoints

### Tasks
```
POST   /api/v1/tasks              Create task
GET    /api/v1/tasks              List tasks (with filters)
GET    /api/v1/tasks/{id}         Get task
PATCH  /api/v1/tasks/{id}         Update task
POST   /api/v1/tasks/{id}/assign  Assign to staff
POST   /api/v1/tasks/{id}/start   Start task
POST   /api/v1/tasks/{id}/complete Complete task
POST   /api/v1/tasks/{id}/delay   Mark as delayed
POST   /api/v1/tasks/auto-assign  Auto-assign pending tasks
```

### Schedules
```
POST   /api/v1/schedules              Create schedule
GET    /api/v1/schedules              List schedules
GET    /api/v1/schedules/{id}         Get schedule
PATCH  /api/v1/schedules/{id}         Update schedule
POST   /api/v1/schedules/{id}/activate Activate schedule
POST   /api/v1/schedules/{id}/pause   Pause schedule
POST   /api/v1/schedules/{id}/generate-tasks Manual task generation
```

### Maintenance
```
POST   /api/v1/maintenance              Create request
GET    /api/v1/maintenance              List requests
GET    /api/v1/maintenance/{id}         Get request
PATCH  /api/v1/maintenance/{id}         Update request
POST   /api/v1/maintenance/{id}/triage  Triage request
POST   /api/v1/maintenance/{id}/start   Start work
POST   /api/v1/maintenance/{id}/complete Complete request
POST   /api/v1/maintenance/{id}/escalate Escalate priority
```

### Dashboard
```
GET    /api/v1/dashboard/summary      Full dashboard summary
GET    /api/v1/dashboard/real-time    Real-time status
GET    /api/v1/dashboard/report       Custom period report
GET    /api/v1/dashboard/report/daily Daily report
GET    /api/v1/dashboard/report/weekly Weekly report
GET    /api/v1/dashboard/metrics/tasks Task metrics
GET    /api/v1/dashboard/metrics/maintenance Maintenance metrics
GET    /api/v1/dashboard/alerts       Critical alerts
```

## Setup & Installation

### Prerequisites
- Python 3.11+
- PostgreSQL
- RabbitMQ (for event streaming)

### Create Virtual Environment

```bash
# Windows
cd housekeeping-maintenance-service
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
cd housekeeping-maintenance-service
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file:

```env
# Application
APP_NAME=housekeeping-maintenance-service
APP_VERSION=1.0.0
DEBUG=true

# Server
HOST=0.0.0.0
PORT=8007

# Database
DATABASE_URL=postgresql://housekeeping_user:housekeeping_password@localhost:5432/housekeeping_db

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
RABBITMQ_EXCHANGE=hospitality_platform

# SLA Configuration (minutes)
CHECKOUT_CLEANING_SLA=60
MAINTENANCE_RESPONSE_SLA=120
CRITICAL_MAINTENANCE_SLA=30
```

### Database Setup

```bash
# Create PostgreSQL database
createdb housekeeping_db

# Tables are created automatically on startup
```

### Run the Service

```bash
# Development
uvicorn app.main:app --reload --port 8007

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8007 --workers 4
```

## Event Integration

### Consumed Events

| Event | Source | Action |
|-------|--------|--------|
| `booking.completed` | Booking Service | Creates checkout cleaning task |
| `booking.cancelled` | Booking Service | Cancels pending tasks |
| `inventory.low_stock` | Inventory Service | Creates restocking task |
| `inventory.critical_stock` | Inventory Service | Creates urgent restocking task |
| `guest.complaint_filed` | Guest Service | Creates maintenance request |

### Published Events

| Event | Trigger | Consumers |
|-------|---------|-----------|
| `task.completed` | Task completion | Analytics, Notifications |
| `task.delayed` | SLA breach | Notifications, Booking |
| `room.ready` | Cleaning complete | Booking Service |
| `maintenance.resolved` | Issue fixed | Inventory, Booking |

## Data Models

### Task
Represents an operational task (cleaning, maintenance, restocking):
- Types: checkout_cleaning, stay_over_cleaning, deep_cleaning, inspection, maintenance_repair, restocking, etc.
- States: pending → assigned → in_progress → completed → verified

### CleaningSchedule
Defines recurring cleaning patterns:
- Recurrence: daily, weekly, biweekly, monthly
- Triggers: time-based, on_checkout, on_checkin

### MaintenanceRequest
Tracks maintenance issues:
- Categories: plumbing, electrical, HVAC, appliance, furniture, safety
- States: reported → triaged → scheduled → in_progress → completed

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## Docker Support

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]
```

## Integration with Other Services

This service is part of a larger hospitality platform microservices architecture:

- **Booking Service** (port 8001): Sends checkout events, consumes room.ready events
- **Inventory Service** (port 8006): Sends stock alerts, consumes maintenance completion
- **Guest Service** (port 8003): Sends complaint events
- **Notification Service**: Consumes delay/alert events
- **Analytics Service**: Consumes all task events for reporting

## License

Proprietary - Part of MSOP Hospitality Platform
