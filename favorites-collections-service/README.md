# Favorites & Collections Service

A FastAPI microservice for managing user favorites and collections in the Smart Hospitality & Retail platform.

## Overview

This service allows authenticated users to:

- **Save and unsave places** (favorites) with idempotent operations
- **Create, update, and delete collections** (e.g., "Summer trip", "Date night")
- **Add and remove places** inside collections
- **List user favorites and collections** with pagination
- **Access public (shareable) collections** via a public identifier

### Important Design Decisions

- **Place IDs are opaque strings** - This service does not validate or store place details. Place IDs are treated as references to external services.
- **Soft deletes** - Favorites and collections are soft-deleted by default for data recovery.
- **Idempotent operations** - Favoriting an already-favorited place or adding an existing place to a collection is not an error.
- **Ownership checks** - Users can only modify their own favorites and collections.

## Project Structure

```
favorites-collections-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection setup
│   ├── dependencies.py      # Dependency injection (auth, etc.)
│   ├── exceptions.py        # Custom exceptions and handlers
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── favorites.py    # Favorite API routes
│   │       ├── collections.py  # Collection API routes
│   │       └── public.py       # Public collection access
│   ├── models/
│   │   ├── __init__.py
│   │   ├── favorite.py         # Favorite SQLAlchemy model
│   │   ├── collection.py       # Collection SQLAlchemy model
│   │   └── collection_item.py  # Collection item model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py           # Common response schemas
│   │   ├── favorite.py         # Favorite Pydantic schemas
│   │   └── collection.py       # Collection Pydantic schemas
│   └── services/
│       ├── __init__.py
│       ├── favorite_service.py    # Favorite business logic
│       └── collection_service.py  # Collection business logic
├── requirements.txt
└── README.md
```

## API Endpoints

### Favorites (`/api/v1/favorites`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List user's favorites (paginated) |
| POST | `/` | Add a place to favorites |
| GET | `/{place_id}` | Get a specific favorite |
| PATCH | `/{place_id}` | Update a favorite's note |
| DELETE | `/{place_id}` | Remove from favorites |
| GET | `/{place_id}/status` | Check if place is favorited |
| POST | `/bulk-status` | Check status for multiple places |
| POST | `/{place_id}/toggle` | Toggle favorite status |

### Collections (`/api/v1/collections`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List user's collections (paginated) |
| POST | `/` | Create a new collection |
| GET | `/{collection_id}` | Get collection with items |
| PATCH | `/{collection_id}` | Update collection metadata |
| DELETE | `/{collection_id}` | Delete a collection |
| POST | `/{collection_id}/regenerate-public-id` | Regenerate share link |
| POST | `/{collection_id}/items` | Add place to collection |
| PATCH | `/{collection_id}/items/{item_id}` | Update item note/position |
| DELETE | `/{collection_id}/items/{item_id}` | Remove item by ID |
| DELETE | `/{collection_id}/places/{place_id}` | Remove item by place ID |
| PUT | `/{collection_id}/items/reorder` | Reorder all items |
| GET | `/containing/{place_id}` | Find collections containing place |

### Public (`/api/v1/public`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/collections/{public_id}` | Get shared collection |
| HEAD | `/collections/{public_id}` | Check if collection exists |

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 13+

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (or create `.env` file):
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/favorites_collections_db
JWT_SECRET_KEY=your-secret-key-here
DEBUG=true
```

4. Run the service:
```bash
uvicorn app.main:app --reload
```

5. Access the API documentation at `http://localhost:8000/docs`

## Database Schema

### favorites
| Column | Type | Description |
|--------|------|-------------|
| user_id | VARCHAR(255) | PK, User ID from auth service |
| place_id | VARCHAR(255) | PK, External place identifier |
| note | VARCHAR(500) | Optional user note |
| created_at | TIMESTAMP | When favorited |
| deleted_at | TIMESTAMP | Soft delete timestamp |

### collections
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | VARCHAR(255) | Owner's user ID |
| public_id | VARCHAR(12) | Shareable identifier |
| name | VARCHAR(255) | Collection name |
| description | TEXT | Optional description |
| cover_image_url | VARCHAR(2048) | Cover image URL |
| is_public | BOOLEAN | Whether publicly accessible |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| deleted_at | TIMESTAMP | Soft delete timestamp |

### collection_items
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| collection_id | UUID | FK to collections |
| place_id | VARCHAR(255) | External place identifier |
| position | INTEGER | Order within collection |
| note | VARCHAR(1000) | User note for this item |
| added_at | TIMESTAMP | When added to collection |
| deleted_at | TIMESTAMP | Soft delete timestamp |

## Authentication

The service expects a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

The token payload should include:
- `user_id` or `sub`: The user's unique identifier
- `email` (optional): User's email address

Configure JWT settings in environment variables:
- `JWT_SECRET_KEY`: Secret key for token validation
- `JWT_ALGORITHM`: Algorithm (default: HS256)

## Error Handling

All errors follow a consistent format:

```json
{
  "success": false,
  "error_code": "NOT_FOUND",
  "message": "Collection not found",
  "details": {
    "resource": "Collection",
    "identifier": "abc123"
  }
}
```

Common error codes:
- `NOT_FOUND` (404): Resource doesn't exist
- `FORBIDDEN` (403): User doesn't have permission
- `VALIDATION_ERROR` (422): Invalid input data
- `CONFLICT` (409): Action conflicts with existing state

## Integration Notes

### Frontend Integration

1. **Favorite buttons**: Use `POST /favorites/{place_id}/toggle` for simple heart button behavior
2. **Bulk status**: When loading a list of places, use `POST /favorites/bulk-status` to efficiently get favorite states
3. **Collections containing**: Use `GET /collections/containing/{place_id}` to show checkmarks in "Add to collection" dialogs
4. **Drag-and-drop**: Use `PUT /collections/{id}/items/reorder` after drag operations

### Other Services

This service:
- Does NOT store place details (fetch from Place Service)
- Does NOT handle bookings (that's Booking Service)
- Does NOT process payments (that's Payment Service)
- ONLY stores user-place relationships and collection metadata

## License

Internal use only - Smart Hospitality & Retail Platform


