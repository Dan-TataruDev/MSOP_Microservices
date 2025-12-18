# Quick Start Guide

## Prerequisites

1. **Node.js** (v18 or higher)
   ```bash
   node --version  # Should be >= 18.0.0
   ```

2. **pnpm** (v8 or higher) - **REQUIRED**
   
   ⚠️ **Important:** This project uses `pnpm` workspaces. You **cannot** use `npm` or `yarn`. The `workspace:*` protocol is pnpm-specific.
   
   ```bash
   # Install pnpm globally
   npm install -g pnpm
   
   # Verify installation
   pnpm --version  # Should be >= 8.0.0
   ```
   
   If you see errors about "workspace:*" protocol, you're using the wrong package manager. Use `pnpm install`, not `npm install`.

## Initial Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   pnpm install
   ```

3. **Set up environment variables:**
   
   Create `.env` files in each app directory or use a root `.env`:
   
   ```bash
   # frontend/.env or frontend/apps/guest/.env
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

4. **Start development servers:**
   ```bash
   # Option 1: Run all apps at once
   pnpm dev
   
   # Option 2: Run apps individually
   pnpm --filter guest dev      # Opens http://localhost:3000
   pnpm --filter business dev   # Opens http://localhost:3001
   pnpm --filter admin dev      # Opens http://localhost:3002
   ```

## Application URLs

Once running, access the applications at:

- **Guest App:** http://localhost:3000
- **Business Dashboard:** http://localhost:3001
- **Admin Interface:** http://localhost:3002

## First Steps

### Guest Application

1. Open http://localhost:3000
2. Browse venues on the home page
3. Use the search functionality to find specific venues
4. Click on a venue to view details
5. Register/Login to make bookings or place orders

### Business Dashboard

1. Open http://localhost:3001
2. Login with business credentials
3. View the operations dashboard
4. Navigate to Inventory, Bookings, Orders, or Analytics

### Admin Interface

1. Open http://localhost:3002
2. Login with admin credentials
3. Access system monitoring and user management

## Backend Integration

**Important:** The frontend expects a backend API running at the URL specified in `VITE_API_BASE_URL`.

The API should implement the following endpoints (as defined in the API client services):

- `/auth/*` - Authentication endpoints
- `/venues/*` - Venue discovery and details
- `/bookings/*` - Booking management
- `/orders/*` - Order management
- `/payments/*` - Payment processing
- `/inventory/*` - Inventory management
- `/analytics/*` - Analytics and metrics

See `packages/api-client/src/services/` for detailed API interface definitions.

## Troubleshooting

### Port Already in Use

If a port is already in use, modify the port in the app's `vite.config.ts`:

```typescript
server: {
  port: 3000, // Change to available port
}
```

### Type Errors

Run type checking:
```bash
pnpm type-check
```

### Build Errors

Clean and rebuild:
```bash
pnpm clean
pnpm install
pnpm build
```

## Next Steps

1. Review the [Architecture Document](../FRONTEND_ARCHITECTURE.md)
2. Set up your backend API to match the frontend API client interfaces
3. Customize the design system components
4. Implement additional features as needed

