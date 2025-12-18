import ApiClient from '../client';

export type CampaignType = 'discount' | 'points_multiplier' | 'bonus_points' | 'free_item' | 'bundle';
export type CampaignStatus = 'draft' | 'scheduled' | 'active' | 'paused' | 'completed' | 'cancelled';

export interface Campaign {
  id: string;
  name: string;
  description: string;
  campaign_type: CampaignType;
  status: CampaignStatus;
  venue_id?: string;
  start_date: string;
  end_date: string;
  target_audience?: string;
  budget?: number;
  spent?: number;
  discount_percentage?: number;
  points_multiplier?: number;
  bonus_points?: number;
  min_purchase?: number;
  max_uses?: number;
  current_uses?: number;
  created_at: string;
  updated_at: string;
}

export interface CampaignCreate {
  name: string;
  description: string;
  campaign_type: CampaignType;
  venue_id?: string;
  start_date: string;
  end_date: string;
  target_audience?: string;
  budget?: number;
  discount_percentage?: number;
  points_multiplier?: number;
  bonus_points?: number;
  min_purchase?: number;
  max_uses?: number;
}

export interface CampaignListResponse {
  items: Campaign[];
  total: number;
  page: number;
  page_size: number;
}

export interface CampaignStats {
  campaign_id: string;
  total_redemptions: number;
  total_revenue_generated: number;
  total_discount_given: number;
  unique_customers: number;
  conversion_rate: number;
}

export class CampaignsService {
  constructor(private client: ApiClient) {}

  async listCampaigns(params?: {
    status?: CampaignStatus;
    venue_id?: string;
    page?: number;
    page_size?: number;
  }): Promise<CampaignListResponse> {
    return this.client.get('/v1/campaigns', { params });
  }

  async getCampaign(campaignId: string): Promise<Campaign> {
    return this.client.get(`/v1/campaigns/${campaignId}`);
  }

  async createCampaign(data: CampaignCreate): Promise<Campaign> {
    return this.client.post('/v1/campaigns', data);
  }

  async updateCampaign(campaignId: string, updates: Partial<CampaignCreate>): Promise<Campaign> {
    return this.client.patch(`/v1/campaigns/${campaignId}`, updates);
  }

  async activateCampaign(campaignId: string): Promise<Campaign> {
    return this.client.post(`/v1/campaigns/${campaignId}/activate`);
  }

  async pauseCampaign(campaignId: string): Promise<Campaign> {
    return this.client.post(`/v1/campaigns/${campaignId}/pause`);
  }

  async getActiveCampaigns(venueId?: string): Promise<Campaign[]> {
    return this.client.get('/v1/campaigns/active', {
      params: venueId ? { venue_id: venueId } : undefined,
    });
  }

  async getCampaignStats(campaignId: string): Promise<CampaignStats> {
    return this.client.get(`/v1/campaigns/${campaignId}/stats`);
  }
}
