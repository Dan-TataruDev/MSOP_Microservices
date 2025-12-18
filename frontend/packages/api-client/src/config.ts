export const API_CONFIG = {
  baseURL: 'http://localhost:8000/api',
  timeout: 30000,
  retryAttempts: 3,
  retryDelay: 1000,
} as const;

// Service-specific base URLs (hardcoded)
// Ports match start-all-services.ps1:
// - Auth Service: 8001
// - Guest Interaction (venues): 8000
// - Booking Reservation: 8002
// - Dynamic Pricing: 8004
// - Payment Billing: 8005
// - Inventory Resource: 8006
// - Favorites Collections: 8007
// - Feedback Sentiment: 8008
// - Marketing Loyalty: 8009
// - BI Analytics: 8010
// - Housekeeping Maintenance: 8011
export const SERVICE_URLS = {
  auth: 'http://localhost:8001/api',
  venues: 'http://localhost:8000/api',
  bookings: 'http://localhost:8002/api',
  orders: 'http://localhost:8000/api',
  payments: 'http://localhost:8005/api',
  inventory: 'http://localhost:8006/api',
  analytics: 'http://localhost:8010/api',
  personalization: 'http://localhost:8000/api',
  favorites: 'http://localhost:8007/api',
  feedback: 'http://localhost:8008/api',
  loyalty: 'http://localhost:8009/api',
  pricing: 'http://localhost:8004/api',
  housekeeping: 'http://localhost:8011/api',
  campaigns: 'http://localhost:8009/api',
  biAnalytics: 'http://localhost:8010/api',
} as const;

export const getApiUrl = (path: string): string => {
  return `${API_CONFIG.baseURL}${path.startsWith('/') ? path : `/${path}`}`;
};

export const getServiceUrl = (service: keyof typeof SERVICE_URLS, path: string): string => {
  const baseUrl = SERVICE_URLS[service];
  return `${baseUrl}${path.startsWith('/') ? path : `/${path}`}`;
};

