import ApiClient from '../client';

export type LoyaltyTier = 'bronze' | 'silver' | 'gold' | 'platinum';

export interface LoyaltyMember {
  id: string;
  guest_id: string;
  program_id: string;
  tier: LoyaltyTier;
  points_balance: number;
  lifetime_points: number;
  next_tier?: LoyaltyTier;
  points_to_next_tier?: number;
  joined_at: string;
}

export interface PointsTransaction {
  id: string;
  points: number;
  description: string;
  source_type: string;
  source_id?: string;
  created_at: string;
}

export interface PointsHistoryResponse {
  items: PointsTransaction[];
  total: number;
  current_balance: number;
}

export interface Campaign {
  id: string;
  name: string;
  description: string;
  campaign_type: 'discount' | 'points_multiplier' | 'bonus_points' | 'free_item';
  status: 'draft' | 'active' | 'paused' | 'completed' | 'cancelled';
  start_date: string;
  end_date: string;
  venue_id?: string;
  target_audience?: string;
  discount_percentage?: number;
  points_multiplier?: number;
  bonus_points?: number;
  created_at: string;
}

export interface CampaignListResponse {
  items: Campaign[];
  total: number;
  page: number;
  page_size: number;
}

export interface Offer {
  id: string;
  name: string;
  description: string;
  offer_type: 'percentage_discount' | 'fixed_discount' | 'free_item' | 'points_reward';
  discount_value?: number;
  points_cost?: number;
  min_order_value?: number;
  valid_from: string;
  valid_until: string;
  is_active: boolean;
}

export class LoyaltyService {
  constructor(private client: ApiClient) {}

  async getMemberStatus(guestId: string): Promise<LoyaltyMember> {
    return this.client.get(`/v1/loyalty/member/${guestId}`);
  }

  async getPointsHistory(guestId: string, limit = 20): Promise<PointsHistoryResponse> {
    return this.client.get(`/v1/loyalty/member/${guestId}/history`, {
      params: { limit },
    });
  }

  async getActiveCampaigns(venueId?: string): Promise<Campaign[]> {
    return this.client.get('/v1/campaigns/active', {
      params: venueId ? { venue_id: venueId } : undefined,
    });
  }

  async listCampaigns(params?: {
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<CampaignListResponse> {
    return this.client.get('/v1/campaigns', { params });
  }

  async getCampaign(campaignId: string): Promise<Campaign> {
    return this.client.get(`/v1/campaigns/${campaignId}`);
  }

  async createCampaign(data: Partial<Campaign>): Promise<Campaign> {
    return this.client.post('/v1/campaigns', data);
  }

  async activateCampaign(campaignId: string): Promise<Campaign> {
    return this.client.post(`/v1/campaigns/${campaignId}/activate`);
  }

  async getAvailableOffers(guestId?: string): Promise<Offer[]> {
    return this.client.get('/v1/offers', {
      params: guestId ? { guest_id: guestId } : undefined,
    });
  }
}
