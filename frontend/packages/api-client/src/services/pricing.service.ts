import ApiClient from '../client';

export type DemandLevel = 'very_low' | 'low' | 'normal' | 'high' | 'very_high';

export interface PriceEstimateRequest {
  venue_id: string;
  venue_type: 'hotel' | 'restaurant' | 'cafe' | 'retail';
  booking_time: string;
  party_size?: number;
  duration_minutes?: number;
}

export interface PriceEstimateResponse {
  venue_id: string;
  estimated_price: number;
  currency: string;
  demand_level: DemandLevel;
  is_peak_time: boolean;
  price_factors: string[];
  valid_until: string;
}

export interface BulkPriceRequest {
  venue_id: string;
  venue_type: 'hotel' | 'restaurant' | 'cafe' | 'retail';
  time_slots: string[];
  party_size?: number;
  duration_minutes?: number;
}

export interface BulkPriceItem {
  time_slot: string;
  estimated_price: string;
  demand_level: DemandLevel;
  is_peak_time: boolean;
}

export interface BulkPriceResponse {
  prices: BulkPriceItem[];
}

export interface PricingRule {
  id: string;
  name: string;
  rule_type: 'time_based' | 'demand_based' | 'event_based' | 'seasonal';
  venue_id?: string;
  is_active: boolean;
  priority: number;
  multiplier_min: number;
  multiplier_max: number;
  conditions: Record<string, any>;
  created_at: string;
}

export interface BasePrice {
  id: string;
  venue_id: string;
  venue_type: string;
  item_category?: string;
  base_price: number;
  currency: string;
  effective_from: string;
  effective_to?: string;
}

export class PricingService {
  constructor(private client: ApiClient) {}

  async getPriceEstimate(request: PriceEstimateRequest): Promise<PriceEstimateResponse> {
    return this.client.post('/v1/pricing/estimate', request);
  }

  async getBulkPrices(request: BulkPriceRequest): Promise<BulkPriceResponse> {
    return this.client.post('/v1/pricing/bulk', request);
  }

  async listRules(venueId?: string): Promise<PricingRule[]> {
    return this.client.get('/v1/rules', {
      params: venueId ? { venue_id: venueId } : undefined,
    });
  }

  async getRule(ruleId: string): Promise<PricingRule> {
    return this.client.get(`/v1/rules/${ruleId}`);
  }

  async listBasePrices(venueId: string): Promise<BasePrice[]> {
    return this.client.get('/v1/base-prices', {
      params: { venue_id: venueId },
    });
  }
}
