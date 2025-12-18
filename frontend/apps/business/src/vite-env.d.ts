/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_AUTH_SERVICE_URL: string;
  readonly VITE_VENUE_SERVICE_URL?: string;
  readonly VITE_BOOKING_SERVICE_URL: string;
  readonly VITE_ORDER_SERVICE_URL?: string;
  readonly VITE_PAYMENT_SERVICE_URL: string;
  readonly VITE_INVENTORY_SERVICE_URL: string;
  readonly VITE_ANALYTICS_SERVICE_URL?: string;
  readonly VITE_PERSONALIZATION_SERVICE_URL?: string;
  readonly VITE_FAVORITES_SERVICE_URL: string;
  readonly VITE_FEEDBACK_SERVICE_URL: string;
  readonly VITE_LOYALTY_SERVICE_URL: string;
  readonly VITE_PRICING_SERVICE_URL: string;
  readonly VITE_HOUSEKEEPING_SERVICE_URL: string;
  readonly VITE_CAMPAIGNS_SERVICE_URL: string;
  readonly VITE_BI_ANALYTICS_SERVICE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

