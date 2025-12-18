import ApiClient from '../client';
import type {
  BusinessMetrics,
  ApiResponse,
  DateRange,
} from '@hospitality-platform/types';

export class AnalyticsService {
  constructor(private client: ApiClient) {}

  async getBusinessMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics>> {
    return this.client.get(`/analytics/business/${businessId}/metrics`, { params: dateRange });
  }

  async getRevenueMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics['revenue']>> {
    return this.client.get(`/analytics/business/${businessId}/revenue`, { params: dateRange });
  }

  async getBookingMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics['bookings']>> {
    return this.client.get(`/analytics/business/${businessId}/bookings`, { params: dateRange });
  }

  async getOrderMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics['orders']>> {
    return this.client.get(`/analytics/business/${businessId}/orders`, { params: dateRange });
  }

  async getSentimentMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics['sentiment']>> {
    return this.client.get(`/analytics/business/${businessId}/sentiment`, { params: dateRange });
  }
}

