export { default as ApiClient } from './client';
export { API_CONFIG, getApiUrl } from './config';
export type { TokenStorage } from './client';

// Services
export { AuthService } from './services/auth.service';
export { VenueService } from './services/venue.service';
export { BookingService } from './services/booking.service';
export { OrderService } from './services/order.service';
export { PaymentService } from './services/payment.service';
export { InventoryService } from './services/inventory.service';
export { AnalyticsService } from './services/analytics.service';
export { PersonalizationService } from './services/personalization.service';
export { FavoritesService } from './services/favorites.service';
export { FeedbackService } from './services/feedback.service';
export { LoyaltyService } from './services/loyalty.service';
export { PricingService } from './services/pricing.service';
export { HousekeepingService } from './services/housekeeping.service';
export { CampaignsService } from './services/campaigns.service';
export { BiAnalyticsService } from './services/bi-analytics.service';

// Create a factory function to initialize all services
import ApiClient from './client';
import { AuthService } from './services/auth.service';
import { VenueService } from './services/venue.service';
import { BookingService } from './services/booking.service';
import { OrderService } from './services/order.service';
import { PaymentService } from './services/payment.service';
import { InventoryService } from './services/inventory.service';
import { AnalyticsService } from './services/analytics.service';
import { PersonalizationService } from './services/personalization.service';
import { FavoritesService } from './services/favorites.service';
import { FeedbackService } from './services/feedback.service';
import { LoyaltyService } from './services/loyalty.service';
import { PricingService } from './services/pricing.service';
import { HousekeepingService } from './services/housekeeping.service';
import { CampaignsService } from './services/campaigns.service';
import { BiAnalyticsService } from './services/bi-analytics.service';
import type { TokenStorage } from './client';

export interface ApiServices {
  auth: AuthService;
  venues: VenueService;
  bookings: BookingService;
  orders: OrderService;
  payments: PaymentService;
  inventory: InventoryService;
  analytics: AnalyticsService;
  personalization: PersonalizationService;
  favorites: FavoritesService;
  feedback: FeedbackService;
  loyalty: LoyaltyService;
  pricing: PricingService;
  housekeeping: HousekeepingService;
  campaigns: CampaignsService;
  biAnalytics: BiAnalyticsService;
}

export function createApiServices(tokenStorage: TokenStorage): ApiServices {
  const client = new ApiClient(tokenStorage);
  return {
    auth: new AuthService(client),
    venues: new VenueService(client),
    bookings: new BookingService(client),
    orders: new OrderService(client),
    payments: new PaymentService(client),
    inventory: new InventoryService(client),
    analytics: new AnalyticsService(client),
    personalization: new PersonalizationService(client),
    favorites: new FavoritesService(client),
    feedback: new FeedbackService(client),
    loyalty: new LoyaltyService(client),
    pricing: new PricingService(client),
    housekeeping: new HousekeepingService(client),
    campaigns: new CampaignsService(client),
    biAnalytics: new BiAnalyticsService(client),
  };
}

