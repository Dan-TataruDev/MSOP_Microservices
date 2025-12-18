# Business Intelligence & Analytics Service

A read-optimized microservice that aggregates data from events emitted by other services to produce dashboards, reports, and KPIs for business users.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Business Intelligence Service                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │   Event      │    │  Aggregation │    │      API Layer           │  │
│  │   Consumer   │───▶│   Service    │───▶│  (Read-Optimized)        │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
│         │                   │                        │                  │
│         ▼                   ▼                        ▼                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Analytics Database                              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │  │
│  │  │  Raw       │  │  Metric    │  │  Realtime  │  │  Reports   │  │  │
│  │  │  Events    │  │  Snapshots │  │  Metrics   │  │            │  │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
              ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
              │  Booking  │   │  Payment  │   │  Other    │
              │  Service  │   │  Service  │   │  Services │
              └───────────┘   └───────────┘   └───────────┘
```

## Design Principles

### 1. Read-Heavy Optimization
- Pre-aggregated metrics for sub-second dashboard queries
- Read replicas for horizontal scaling
- Caching layer for frequently accessed KPIs
- Efficient database indexes for time-series queries

### 2. Eventual Consistency
- Accepts 5-15 minute data freshness lag
- Decoupled from transactional workloads
- Asynchronous event processing
- No real-time dependencies on source services

### 3. Non-Interference
- Separate database from transactional services
- Event-driven ingestion (no direct API calls)
- Background aggregation jobs
- No impact on booking/payment performance

## Data Ingestion

### Event Sources
The service consumes events from:
- **Booking Service**: booking.created, booking.confirmed, booking.cancelled
- **Payment Service**: payment.completed, payment.failed, refund.processed
- **Inventory Service**: room.status_changed, inventory.updated
- **Feedback Service**: feedback.submitted, sentiment.analyzed
- **Loyalty Service**: loyalty.points_earned, loyalty.tier_changed
- **Housekeeping Service**: task.completed, maintenance.resolved
- **Pricing Service**: price.updated, rate.optimized

### Ingestion Flow
```
Event Bus (RabbitMQ) → Event Consumer → Raw Event Storage → Aggregation Job → Metric Snapshots
```

1. Events are consumed from message broker
2. Raw events stored for audit and reprocessing
3. Background jobs aggregate into metrics
4. Pre-computed metrics served to dashboards

## Metrics Computed

### Revenue Metrics
- `total_revenue` - Total revenue in period
- `average_order_value` - Average transaction value
- `revpar` - Revenue per available room
- `revenue_per_room` - Revenue breakdown by room type

### Booking Metrics
- `total_bookings` - Number of bookings
- `booking_conversion_rate` - Search to booking ratio
- `cancellation_rate` - Cancelled / Total bookings
- `average_lead_time` - Days between booking and stay

### Occupancy Metrics
- `occupancy_rate` - Rooms occupied / Available
- `average_daily_rate` - Average room rate
- `revpar` - RevPAR calculation

### Guest Satisfaction
- `guest_satisfaction` - Average rating (1-5)
- `net_promoter_score` - NPS calculation
- `repeat_guest_rate` - Returning guests %

### Operational Metrics
- `payment_success_rate` - Successful payments %
- `housekeeping_efficiency` - Tasks completed on time
- `maintenance_response_time` - Average resolution time

## API Endpoints

### Dashboards
```
GET /api/v1/dashboard              # Main KPI dashboard
GET /api/v1/dashboard/revenue      # Revenue-focused view
GET /api/v1/dashboard/operations   # Operations metrics
```

### Metrics
```
GET /api/v1/metrics/{metric_type}           # Single metric
GET /api/v1/metrics/{metric_type}/timeseries # Time series data
POST /api/v1/metrics/query                   # Multi-metric query
```

### Reports
```
POST /api/v1/reports                    # Create report
GET /api/v1/reports                     # List reports
GET /api/v1/reports/{id}                # Get report
POST /api/v1/reports/scheduled          # Create scheduled report
```

### Admin
```
GET /api/v1/admin/stats                 # System statistics
POST /api/v1/admin/aggregation/run      # Trigger aggregation
GET /api/v1/admin/checkpoints           # Processing status
```

## Data Model

### Granularity Levels
- **Hourly** - Retained for 90 days
- **Daily** - Retained for 1 year
- **Weekly** - Retained for 2 years
- **Monthly** - Retained for 5 years

### Storage Strategy
```sql
-- Pre-aggregated snapshots for fast queries
metric_snapshots (
    metric_type, granularity, period_start, period_end,
    value, count, min_value, max_value, dimensions
)

-- Raw events for audit/reprocessing
ingested_events (
    event_id, event_type, source, payload,
    event_timestamp, processed, processed_at
)

-- Generated reports
reports (
    report_type, name, data, summary,
    period_start, period_end, status
)
```

## Configuration

```env
# Database (separate from transactional DBs)
DATABASE_URL=postgresql://analytics_user:pass@localhost:5432/bi_analytics_db

# Read replica (optional)
READ_REPLICA_URL=postgresql://analytics_user:pass@replica:5432/bi_analytics_db

# Caching
REDIS_URL=redis://localhost:6379/1
CACHE_TTL_SECONDS=300
CACHE_KPI_TTL_SECONDS=60

# Event broker
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
RABBITMQ_EXCHANGE=hospitality_platform

# Aggregation
AGGREGATION_INTERVAL_MINUTES=5
BATCH_SIZE=1000
```

## Running the Service

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python -m app.main

# Or with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload
```

## Scaling Considerations

### Horizontal Scaling
- Multiple API instances behind load balancer
- Read replicas for database reads
- Partitioned event consumer groups

### Performance Optimization
- Redis caching for hot KPIs
- Pre-computed hourly/daily aggregates
- Database connection pooling
- Query optimization with proper indexes

### Data Lifecycle
- Automatic cleanup of old raw events
- Rollup from fine to coarse granularity
- Archive to cold storage if needed

## Integration with Frontend

The service exposes chart-ready data:
```json
{
  "dashboard_id": "main",
  "revenue_kpis": [
    {
      "id": "total_revenue",
      "title": "Total Revenue",
      "value": 125000,
      "formatted_value": "$125,000.00",
      "change_percent": 12.5,
      "trend": "up",
      "sparkline": [100, 110, 105, 120, 125]
    }
  ]
}
```

## Port
Default: **8010**
