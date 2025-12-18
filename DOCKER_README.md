# Docker Compose Setup Guide

This Docker Compose configuration allows you to run all microservices and the frontend together in containers.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+

## Quick Start

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Stop all services:**
   ```bash
   docker-compose down
   ```

4. **Stop and remove volumes (clean slate):**
   ```bash
   docker-compose down -v
   ```

## Services

### Infrastructure Services
- **PostgreSQL** (port 5432) - Database for all microservices
- **RabbitMQ** (ports 5672, 15672) - Message queue for event streaming
  - Management UI: http://localhost:15672 (guest/guest)

### Backend Microservices
- **Auth Service** - http://localhost:8001/docs
- **Guest Interaction Service** - http://localhost:8000/docs
- **Booking Reservation Service** - http://localhost:8002/docs
- **Dynamic Pricing Service** - http://localhost:8004/docs
- **Payment Billing Service** - http://localhost:8005/docs
- **Inventory Resource Service** - http://localhost:8006/docs
- **Favorites Collections Service** - http://localhost:8007/docs
- **Feedback Sentiment Service** - http://localhost:8008/docs
- **Marketing Loyalty Service** - http://localhost:8009/docs
- **BI Analytics Service** - http://localhost:8010/docs
- **Housekeeping Maintenance Service** - http://localhost:8011/docs

### Frontend
- **Frontend Application** - http://localhost:3000

## Environment Variables

Services are configured with environment variables in `docker-compose.yml`. Key variables:

- `DATABASE_URL` - PostgreSQL connection string
- `RABBITMQ_URL` - RabbitMQ connection string
- `AUTH_SERVICE_URL` - Auth service URL for other services
- `JWT_SECRET_KEY` - JWT secret (change in production!)

## Database Setup

The `init-postgres.sh` script automatically creates:
- All required databases
- Database users with proper permissions
- Schema privileges

Databases are initialized on first startup.

## Building Images

To rebuild all images:
```bash
docker-compose build
```

To rebuild a specific service:
```bash
docker-compose build auth-service
```

## Health Checks

All services include health checks. Check service status:
```bash
docker-compose ps
```

## Troubleshooting

### Services won't start
1. Check if ports are already in use:
   ```bash
   docker-compose ps
   ```
2. Check logs:
   ```bash
   docker-compose logs [service-name]
   ```

### Database connection issues
1. Ensure PostgreSQL is healthy:
   ```bash
   docker-compose ps postgres
   ```
2. Check PostgreSQL logs:
   ```bash
   docker-compose logs postgres
   ```

### Frontend not loading
1. Check if frontend container is running:
   ```bash
   docker-compose ps frontend
   ```
2. Check frontend build logs:
   ```bash
   docker-compose logs frontend
   ```

### Rebuild after code changes
```bash
docker-compose up -d --build
```

## Development vs Production

This setup is configured for **development**. For production:

1. Change `JWT_SECRET_KEY` to a secure random string
2. Use environment-specific database credentials
3. Enable SSL/TLS for services
4. Configure proper CORS origins
5. Use secrets management for sensitive data
6. Set up proper logging and monitoring
7. Configure resource limits for containers

## Network

All services are on the `hospitality_network` bridge network, allowing them to communicate using service names (e.g., `auth-service:8001`).

## Volumes

- `postgres_data` - PostgreSQL data persistence
- `rabbitmq_data` - RabbitMQ data persistence

Data persists between container restarts. Use `docker-compose down -v` to remove volumes.
