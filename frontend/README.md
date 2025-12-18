# Smart Hospitality & Retail Platform - Frontend

This is the frontend monorepo for the Smart Hospitality & Retail Platform, containing three main applications and shared packages.

## Structure

- `apps/guest` - Guest-facing progressive web application
- `apps/business` - Business dashboard application
- `apps/admin` - Internal/admin interface
- `packages/` - Shared packages (design system, API client, utilities, types)

## Getting Started

### Prerequisites

- **Node.js** >= 18.0.0
- **pnpm** >= 8.0.0 (required - this project uses pnpm workspaces, npm will not work)

### Installation

**Important:** This project requires `pnpm`, not `npm`. The workspace dependencies use pnpm's `workspace:*` protocol which npm does not support.

```bash
# Step 1: Install pnpm globally (if you haven't already)
npm install -g pnpm

# Step 2: Verify pnpm is installed
pnpm --version  # Should show >= 8.0.0

# Step 3: Install all dependencies
cd frontend
pnpm install
```

**Note:** If you see an error about "workspace:*" protocol, you're using npm instead of pnpm. Make sure to use `pnpm install`, not `npm install`.

### Environment Configuration

Create `.env` files in each application directory (or use a root `.env` file):

```bash
# .env (or apps/guest/.env, apps/business/.env, apps/admin/.env)
VITE_API_BASE_URL=http://localhost:8000/api
```

### Development

Run all applications in development mode:

```bash
pnpm dev
```

Run a specific application:

```bash
pnpm --filter guest dev
pnpm --filter business dev
pnpm --filter admin dev
```

### Building

Build all applications:

```bash
pnpm build
```

Build a specific application:

```bash
pnpm --filter guest build
```

### Type Checking

```bash
pnpm type-check
```

### Linting

```bash
pnpm lint
```

## Applications

### Guest Application

Mobile-first PWA for customers to discover venues, make bookings, place orders, and manage their experiences.

**Tech Stack:**
- React 18 + TypeScript
- Vite
- React Router
- React Query
- Zustand
- Tailwind CSS
- WebSocket for real-time updates

### Business Dashboard

Desktop-first management interface for businesses to manage operations, inventory, bookings, and analytics.

**Tech Stack:**
- React 18 + TypeScript
- Vite
- React Router
- React Query
- Zustand
- Tailwind CSS
- Recharts for analytics

### Admin Interface

Secure administrative interface for platform oversight, user management, and compliance.

**Tech Stack:**
- React 18 + TypeScript
- Vite
- React Router
- React Query
- Zustand
- Tailwind CSS

## Project Structure

```
frontend/
├── apps/
│   ├── guest/          # Guest-facing PWA
│   ├── business/       # Business dashboard
│   └── admin/          # Admin interface
├── packages/
│   ├── types/          # Shared TypeScript types
│   ├── api-client/     # API client with services
│   ├── utils/          # Utility functions
│   └── design-system/  # Shared UI components
└── package.json        # Root package.json with workspace config
```

## Key Features

### Guest Application
- ✅ Venue discovery and search
- ✅ Personalized recommendations
- ✅ Booking management
- ✅ Order placement and tracking
- ✅ User profile and preferences
- ✅ PWA support with offline capabilities

### Business Dashboard
- ✅ Operations overview dashboard
- ✅ Inventory management
- ✅ Booking management
- ✅ Order management
- ✅ Analytics and reporting
- ✅ Real-time updates

### Admin Interface
- ✅ System health monitoring
- ✅ User management
- ✅ Business account management
- ✅ Platform oversight

## Shared Packages

### @hospitality-platform/types
Comprehensive TypeScript type definitions for all domain models, API responses, and data structures.

### @hospitality-platform/api-client
Centralized API client with:
- Automatic token management and refresh
- Request/response interceptors
- Error handling
- Service classes for each backend microservice

### @hospitality-platform/utils
Utility functions for:
- Formatting (currency, dates, numbers)
- Validation (email, phone, passwords)
- Secure storage management

### @hospitality-platform/design-system
Shared UI components following design system patterns (currently includes Button component, can be extended).

## Development Workflow

1. **Start Development Servers:**
   ```bash
   # Run all apps
   pnpm dev
   
   # Or run individually
   pnpm --filter guest dev      # http://localhost:3000
   pnpm --filter business dev   # http://localhost:3001
   pnpm --filter admin dev      # http://localhost:3002
   ```

2. **Make Changes:**
   - Edit files in `apps/` for application-specific code
   - Edit files in `packages/` for shared code
   - Changes to packages are automatically reflected in apps (via workspace links)

3. **Type Checking:**
   ```bash
   pnpm type-check
   ```

4. **Building for Production:**
   ```bash
   pnpm build
   ```

## Architecture

See [FRONTEND_ARCHITECTURE.md](../FRONTEND_ARCHITECTURE.md) for detailed architecture documentation.

## Technology Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **React Query (TanStack Query)** - Server state management
- **Zustand** - Client state management
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **Recharts** - Chart library (business dashboard)
- **pnpm** - Package manager with workspace support

## Next Steps

1. Set up backend API endpoints matching the API client service interfaces
2. Implement WebSocket connections for real-time updates
3. Add more design system components as needed
4. Implement additional features per the architecture document
5. Set up CI/CD pipelines for automated testing and deployment

