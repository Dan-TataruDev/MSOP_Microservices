## MSOP Hospitality Platform

A full‑stack hospitality platform for search, booking, ordering, loyalty, and business/admin operations. The repo contains a React frontend (with admin and business consoles) and a TypeScript API client that can talk to real backend services or rich in‑memory mock services.

---

### Project Structure

- **root**
  - **frontend/** – main web application (guest, business, admin)
    - **apps/main/** – React app (Vite) with routes and layouts
    - **packages/api-client/** – typed Axios client + mock services
    - **packages/utils/** – shared formatting/utilities
  - **cleanup-all-services.ps1** – helper script for cleaning generated service files

_(Backend services are assumed external; only the frontend and API client live in this repo.)_

---

### Requirements

- **Node.js**: 18+ (recommended 18 LTS or newer)
- **Package manager**: `pnpm` (preferred) or `npm`/`yarn`
- **Git** and a modern browser

---

### Getting Started (Frontend)

#### 1. Install dependencies

From the repo root:

```bash
cd frontend
pnpm install   # or: npm install / yarn install
```

#### 2. Environment configuration

Inside `frontend/apps/main/` create a `.env` file (or `.env.local`) with at least:

```bash
VITE_API_BASE_URL=
VITE_USE_MOCK_LOYALTY=true
VITE_USE_MOCK_FAVORITES=true
VITE_USE_MOCK_PAYMENT=true
VITE_USE_MOCK_BOOKING=true
VITE_USE_MOCK_ORDER=true
VITE_USE_MOCK_PERSONALIZATION=true
# Optional: additional toggles if added later
# VITE_USE_MOCK_ANALYTICS=true
```

- **Empty or missing `VITE_API_BASE_URL`** enables most mock services by default.
- Per‑service flags (like `VITE_USE_MOCK_LOYALTY`) force a specific mock implementation even when a backend exists.

This lets you run the app with **rich mock data** for:

- **Guest**: search, venue details, bookings, orders, favorites, loyalty, payments, personalization
- **Business**: bookings, orders, inventory, pricing, tasks, feedback, campaigns, analytics
- **Admin**: platform analytics and system stats

#### 3. Run the dev server

```bash
cd frontend/apps/main
pnpm dev      # or: npm run dev / yarn dev
```

By default Vite serves at `http://localhost:5173` (shown in the terminal output).

---

### Authentication & Roles

The app supports multiple roles that control which layouts and navigation are visible:

- **Guest (unauthenticated)**
  - Access to home, search, venue pages, registration, login.
- **User (authenticated guest)**
  - Access to favorites, loyalty, payments, preferences, booking history.
- **Business / Manager**
  - Access to `/business` (business dashboard) and related pages: bookings, orders, inventory, pricing, tasks, feedback, campaigns, analytics.
- **Admin**
  - Access to `/admin` (admin dashboard), analytics, users, businesses.
  - Also allowed to enter the business area from the main header.

The `useAuthStore` Zustand store holds:

- **`user`** – user profile and `roles` array
- **`tokens`** – auth tokens for API requests
- **`businessContext`** – selected business/venue for business pages

When logging in via the **Login** page, tokens and user data are stored in `useAuthStore`, and you are redirected to the **main page (`/`)**. From there the header exposes extra navigation items depending on your role.

---

### Mock Services Overview

Most API services have an accompanying **mock service** that returns in‑memory data with realistic structures. The selection logic is usually:

- **If `VITE_API_BASE_URL` is not set** → use **mock** service by default.
- **If specific `VITE_USE_MOCK_xxx` is set** → force mock for that domain.

Key mock domains:

- **Loyalty** – member status, points history, offers, redemption
- **Favorites** – venue favorites tied to mock venues
- **Payments & Billing** – payments, invoices, billing records
- **Bookings** – guest bookings and business‑side bookings
- **Orders** – guest orders and business‑side orders
- **Personalization** – guest profiles, preferences, segments, signals
- **Analytics (business)** – business KPIs and time series
- **Inventory** – stock levels and alerts per product
- **Pricing** – rules, base prices, and price estimator
- **Housekeeping / Tasks** – task lists, pending/overdue tasks, start/complete
- **Feedback** – guest feedback, sentiment, venue insights
- **Campaigns** – marketing campaigns and stats

This allows you to explore almost all pages (guest, business, admin) without a running backend.

---

### Key Frontend Areas

- **Guest app** (`frontend/apps/main/src/pages/guest`)
  - **Home**: marketing hero, search, recommendations, trending
  - **Loyalty**: points, history, offers, interactive redemption
  - **Favorites**: rich venue cards for saved places
  - **Payments/Billing**: mock payments & invoices
  - **Bookings & Orders**: history and details
  - **Profile & Preferences**: personalization and settings

- **Business app** (`frontend/apps/main/src/pages/business`)
  - **Dashboard**: revenue, bookings, orders, sentiment
  - **Bookings**: upcoming and past guest bookings
  - **Orders**: restaurant/room‑service style orders
  - **Inventory**: stock tables with low‑stock highlighting
  - **Pricing**: price estimator, active rules, base prices
  - **Tasks**: housekeeping/maintenance tasks with filters
  - **Feedback**: sentiment‑aware feedback list and insights
  - **Campaigns**: marketing campaign management
  - **Analytics**: charts and KPIs powered by mock analytics data

- **Admin app** (`frontend/apps/main/src/pages/admin`)
  - **Dashboard**: platform‑wide KPIs and system health
  - **Analytics**: BI views of revenue/operations metrics
  - **Users & Businesses**: management pages

---

### Running With a Real Backend

Once backend services are available, point the API client to them:

```bash
# frontend/apps/main/.env
VITE_API_BASE_URL=https://api.your-backend.com

# Optionally disable some mocks explicitly
VITE_USE_MOCK_LOYALTY=false
VITE_USE_MOCK_BOOKING=false
# ...etc
```

Service classes in `packages/api-client/src/services` use this base URL and per‑service URLs from `getServiceUrl` to communicate with the backend.

---

### Common Scripts

All run from `frontend/` unless noted.

- **Install deps**
  - **pnpm**: `pnpm install`
  - **npm**: `npm install`
- **Development server**
  - `cd apps/main && pnpm dev`
- **Build**
  - `cd apps/main && pnpm build`
- **Preview production build**
  - `cd apps/main && pnpm preview`

(If you use `npm` or `yarn`, replace `pnpm` with your preferred tool.)

---

### Code Style & Quality

- **Language**: TypeScript throughout the frontend and API client.
- **UI**: TailwindCSS utility classes + custom `Card`, `Button`, `Input` components.
- **State**: `useAuthStore` (Zustand) for auth and context; most data via **TanStack Query**.
- **Formatting**: Keep imports minimal and avoid unused symbols; prefer small, readable components and hooks.

---

### Contributing / Local Changes

- **Branches**: create feature branches from `master`.
- **Commits**: keep messages concise and focused on intent ("add business pricing mocks", "fix admin redirect").
- **Testing**: manually verify affected pages (guest, business, admin) when touching shared code like the API client or auth store.

---

### Notes

- The project is built to be **safe to demo without a backend**: enabling mocks gives you fully populated dashboards for guests, businesses, and admins.
- As backend endpoints become available, you can gradually turn off mocks per service and rely on real data without changing the UI components.
