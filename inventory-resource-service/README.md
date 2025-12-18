# Inventory & Resource Management Service

Manages stock levels, room availability, table capacity, and resources for hospitality operations.

## Features

- **Inventory Management**: Track stock levels with automatic low-stock and critical-stock alerts
- **Room Availability**: Real-time room status tracking with booking integration
- **Table Capacity**: Restaurant table management with availability queries
- **Event-Driven**: Consumes events from booking, housekeeping, and supplier services; emits alerts for restocking

## Quick Start

```bash
pip install -r requirements.txt
python -m app.main
```

API docs available at `http://localhost:8006/docs`

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/inventory/items` | List inventory items |
| `POST /api/v1/inventory/items/{id}/adjust` | Adjust stock level |
| `GET /api/v1/inventory/alerts/low-stock` | Get low-stock alerts |
| `GET /api/v1/rooms/venue/{id}/availability` | Room availability summary |
| `GET /api/v1/tables/venue/{id}/availability` | Table availability summary |

## Events

**Emits**: `inventory.low_stock`, `inventory.critical_stock`, `inventory.restock_required`, `resource.room_status_changed`, `resource.table_status_changed`

**Consumes**: `booking.confirmed`, `booking.cancelled`, `housekeeping.completed`, `supplier.delivery`


