/**
 * Mock Analytics Service
 * Provides mock business analytics data for development.
 */
import type { BusinessMetrics, ApiResponse, DateRange } from '@hospitality-platform/types';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Generate date labels for charts
const generateDateLabels = (days: number) => {
  const labels = [];
  for (let i = days; i >= 0; i--) {
    const date = new Date(Date.now() - i * 24 * 60 * 60 * 1000);
    labels.push(date.toISOString().split('T')[0]);
  }
  return labels;
};

const dateLabels = generateDateLabels(30);

const MOCK_BUSINESS_METRICS: BusinessMetrics = {
  revenue: {
    total: 47850,
    change: 5230,
    changePercent: 12.3,
    byPeriod: dateLabels.map(date => ({ date, value: 1200 + Math.floor(Math.random() * 800) })),
  },
  bookings: {
    total: 156,
    confirmed: 142,
    pending: 8,
    cancelled: 6,
    byStatus: { confirmed: 142, pending: 8, cancelled: 6, completed: 89 },
    byPeriod: dateLabels.map(date => ({ date, value: 3 + Math.floor(Math.random() * 8) })),
  },
  orders: {
    total: 324,
    completed: 298,
    pending: 18,
    cancelled: 8,
    averageOrderValue: 45.75,
    byStatus: { completed: 298, pending: 18, cancelled: 8, preparing: 12, delivered: 286 },
    byPeriod: dateLabels.map(date => ({ date, value: 8 + Math.floor(Math.random() * 12) })),
  },
  sentiment: {
    averageScore: 4.3,
    totalReviews: 89,
    trend: 'improving',
    distribution: { 5: 42, 4: 28, 3: 12, 2: 5, 1: 2 },
  },
};

export class MockAnalyticsService {
  async getBusinessMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics>> {
    await delay(400);
    return {
      data: MOCK_BUSINESS_METRICS,
      message: 'Metrics retrieved successfully',
    };
  }

  async getRevenueMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics['revenue']>> {
    await delay(300);
    return {
      data: MOCK_BUSINESS_METRICS.revenue,
      message: 'Revenue metrics retrieved',
    };
  }

  async getBookingMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics['bookings']>> {
    await delay(300);
    return {
      data: MOCK_BUSINESS_METRICS.bookings,
      message: 'Booking metrics retrieved',
    };
  }

  async getOrderMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics['orders']>> {
    await delay(300);
    return {
      data: MOCK_BUSINESS_METRICS.orders,
      message: 'Order metrics retrieved',
    };
  }

  async getSentimentMetrics(businessId: string, dateRange: DateRange): Promise<ApiResponse<BusinessMetrics['sentiment']>> {
    await delay(300);
    return {
      data: MOCK_BUSINESS_METRICS.sentiment,
      message: 'Sentiment metrics retrieved',
    };
  }
}
