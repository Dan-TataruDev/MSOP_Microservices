import ApiClient from '../client';
import { getServiceUrl } from '../config';

export type MetricType = 
  | 'total_revenue' | 'average_order_value' | 'revpar' | 'revenue_per_room'
  | 'total_bookings' | 'booking_conversion_rate' | 'cancellation_rate'
  | 'occupancy_rate' | 'adr'
  | 'guest_satisfaction' | 'nps'
  | 'payment_success_rate' | 'housekeeping_efficiency' | 'maintenance_response_time' | 'check_in_time';

export type Granularity = 'hourly' | 'daily' | 'weekly' | 'monthly';

export interface MetricValue {
  value: number;
  change: number;
  change_percent: number;
  trend: 'up' | 'down' | 'stable';
}

export interface KPIDashboard {
  revenue: {
    total_revenue: MetricValue;
    average_order_value: MetricValue;
    revpar: MetricValue;
  };
  bookings: {
    total_bookings: MetricValue;
    conversion_rate: MetricValue;
    cancellation_rate: MetricValue;
  };
  occupancy: {
    occupancy_rate: MetricValue;
    adr: MetricValue;
  };
  satisfaction: {
    average_rating: MetricValue;
    nps: MetricValue;
  };
  operations: {
    payment_success_rate: MetricValue;
    housekeeping_efficiency: MetricValue;
  };
  period: {
    start: string;
    end: string;
  };
}

export interface TimeSeriesPoint {
  timestamp: string;
  value: number;
}

export interface TimeSeriesData {
  metric_type: MetricType;
  granularity: Granularity;
  data_points: TimeSeriesPoint[];
}

export class BiAnalyticsService {
  constructor(private client: ApiClient) {}

  async getKPIDashboard(params?: {
    date_from?: string;
    date_to?: string;
    compare?: boolean;
  }): Promise<KPIDashboard> {
    const url = getServiceUrl('biAnalytics', '/v1/dashboards/dashboard');
    return this.client.get(url, { params });
  }

  async getMetric(metricType: MetricType, granularity: Granularity = 'daily'): Promise<MetricValue> {
    const url = getServiceUrl('biAnalytics', `/v1/dashboards/metrics/${metricType}`);
    return this.client.get(url, {
      params: { granularity },
    });
  }

  async getMetricTimeSeries(
    metricType: MetricType,
    periodStart: string,
    periodEnd: string,
    granularity: Granularity = 'daily'
  ): Promise<TimeSeriesData> {
    const url = getServiceUrl('biAnalytics', `/v1/dashboards/metrics/${metricType}/timeseries`);
    return this.client.get(url, {
      params: {
        granularity,
        period_start: periodStart,
        period_end: periodEnd,
      },
    });
  }

  async getRevenueDashboard(params?: {
    date_from?: string;
    date_to?: string;
  }): Promise<{
    period: { start: string; end: string };
    metrics: Record<string, MetricValue>;
    revenue_trend: TimeSeriesData;
  }> {
    const url = getServiceUrl('biAnalytics', '/v1/dashboards/dashboard/revenue');
    return this.client.get(url, { params });
  }

  async getOperationsDashboard(params?: {
    date_from?: string;
    date_to?: string;
  }): Promise<{
    period: { start: string; end: string };
    metrics: Record<string, MetricValue>;
  }> {
    const url = getServiceUrl('biAnalytics', '/v1/dashboards/dashboard/operations');
    return this.client.get(url, { params });
  }

  // Admin endpoints
  async getSystemStats(): Promise<{
    events: {
      total: number;
      processed: number;
      pending: number;
      by_source: Record<string, number>;
    };
    metrics: {
      by_granularity: Record<string, number>;
    };
    data_freshness: {
      latest_event: string | null;
      lag_seconds: number | null;
    };
    config: {
      aggregation_interval_minutes: number;
      batch_size: number;
    };
  }> {
    const url = getServiceUrl('biAnalytics', '/v1/admin/stats');
    return this.client.get(url);
  }

  async triggerAggregation(granularity: Granularity = 'hourly'): Promise<{ message: string }> {
    const url = getServiceUrl('biAnalytics', '/v1/admin/aggregation/run');
    return this.client.post(url, null, {
      params: { granularity },
    });
  }
}
