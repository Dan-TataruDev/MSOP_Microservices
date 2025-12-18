import ApiClient from '../client';

export interface FeedbackCreate {
  venue_id: string;
  booking_id?: string;
  category: 'service' | 'food' | 'ambiance' | 'cleanliness' | 'value' | 'overall';
  rating: number;
  comment?: string;
  is_anonymous?: boolean;
}

export interface SentimentResult {
  sentiment: 'positive' | 'neutral' | 'negative';
  confidence: number;
  key_phrases?: string[];
}

export interface FeedbackResponse {
  id: string;
  feedback_reference: string;
  venue_id: string;
  guest_id?: string;
  booking_id?: string;
  category: string;
  rating: number;
  comment?: string;
  status: 'pending' | 'analyzed' | 'reviewed' | 'responded';
  sentiment?: SentimentResult;
  created_at: string;
  analyzed_at?: string;
}

export interface FeedbackListResponse {
  items: FeedbackResponse[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface InsightsSummary {
  total_feedback: number;
  average_rating: number;
  sentiment_distribution: {
    positive: number;
    neutral: number;
    negative: number;
  };
  trending_topics: string[];
  period: { start: string; end: string };
}

export interface VenueInsights {
  venue_id: string;
  total_feedback: number;
  average_rating: number;
  sentiment_distribution: {
    positive: number;
    neutral: number;
    negative: number;
  };
  vs_platform_average: number;
  top_positive_topics: string[];
  areas_for_improvement: string[];
}

export class FeedbackService {
  constructor(private client: ApiClient) {}

  async submitFeedback(data: FeedbackCreate): Promise<FeedbackResponse> {
    return this.client.post('/v1/feedback', data);
  }

  async getFeedback(reference: string): Promise<FeedbackResponse> {
    return this.client.get(`/v1/feedback/${reference}`);
  }

  async getFeedbackStatus(reference: string): Promise<{
    feedback_reference: string;
    status: string;
    sentiment?: SentimentResult;
    analyzed_at?: string;
  }> {
    return this.client.get(`/v1/feedback/${reference}/status`);
  }

  async listFeedback(params?: {
    venue_id?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<FeedbackListResponse> {
    return this.client.get('/v1/feedback', { params });
  }

  async getInsightsSummary(params?: {
    venue_id?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<InsightsSummary> {
    return this.client.get('/v1/insights/summary', { params });
  }

  async getVenueInsights(venueId: string): Promise<VenueInsights> {
    return this.client.get(`/v1/insights/venues/${venueId}`);
  }
}
