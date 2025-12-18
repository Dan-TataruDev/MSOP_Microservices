import ApiClient from '../client';
import { MockAnalyticsService } from './mock-analytics.service';
import type {
  BusinessMetrics,
  ApiResponse,
  DateRange,
} from '@hospitality-platform/types';

const USE_MOCK = !import.meta.env.VITE_API_BASE_URL;
const mockService = new MockAnalyticsService();

export class AnalyticsService {
  constructor(private client: ApiClient) {}

  async getBusinessMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics>> {
    if (USE_MOCK) return mockService.getBusinessMetrics(businessId, dateRange);
    return this.client.get(`/analytics/business/${businessId}/metrics`, { params: dateRange });
  }

  async getRevenueMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics['revenue']>> {
    if (USE_MOCK) return mockService.getRevenueMetrics(businessId, dateRange);
    return this.client.get(`/analytics/business/${businessId}/revenue`, { params: dateRange });
  }

  async getBookingMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics['bookings']>> {
    if (USE_MOCK) return mockService.getBookingMetrics(businessId, dateRange);
    return this.client.get(`/analytics/business/${businessId}/bookings`, { params: dateRange });
  }

  async getOrderMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics['orders']>> {
    if (USE_MOCK) return mockService.getOrderMetrics(businessId, dateRange);
    return this.client.get(`/analytics/business/${businessId}/orders`, { params: dateRange });
  }

  async getSentimentMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics['sentiment']>> {
    if (USE_MOCK) return mockService.getSentimentMetrics(businessId, dateRange);
    return this.client.get(`/analytics/business/${businessId}/sentiment`, { params: dateRange });
  }
}

