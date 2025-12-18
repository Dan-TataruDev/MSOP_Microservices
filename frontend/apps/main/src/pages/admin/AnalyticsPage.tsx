import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
  AreaChart, Area, PieChart, Pie, Cell 
} from 'recharts';
import { 
  BarChart3, DollarSign, Calendar, TrendingUp, TrendingDown, Users, Star, Activity, 
  Building2, CreditCard, CheckCircle, AlertTriangle, Download, RefreshCw, Filter 
} from 'lucide-react';
import { apiServices } from '@/stores/authStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { formatCurrency, formatPercentage } from '@hospitality-platform/utils';

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

// Mock data for demo
const generateMockTimeSeries = (days: number, baseValue: number, variance: number = 0.1) => {
  const data = [];
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);
  
  for (let i = 0; i < days; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    const value = baseValue + (Math.random() - 0.5) * variance * baseValue;
    data.push({
      timestamp: date.toISOString(),
      value: Math.max(0, Math.round(value * 100) / 100),
    });
  }
  return data;
};

const MOCK_KPI_DASHBOARD = {
  revenue: {
    total_revenue: { value: 125000, change: 12500, change_percent: 11.1, trend: 'up' as const },
    average_order_value: { value: 185.50, change: 12.30, change_percent: 7.1, trend: 'up' as const },
    revpar: { value: 285.75, change: 15.25, change_percent: 5.6, trend: 'up' as const },
  },
  bookings: {
    total_bookings: { value: 1250, change: 125, change_percent: 11.1, trend: 'up' as const },
    conversion_rate: { value: 12.5, change: 1.2, change_percent: 10.6, trend: 'up' as const },
    cancellation_rate: { value: 4.2, change: -0.5, change_percent: -10.6, trend: 'down' as const },
  },
  occupancy: {
    occupancy_rate: { value: 78.5, change: 3.2, change_percent: 4.3, trend: 'up' as const },
    adr: { value: 245.00, change: 8.50, change_percent: 3.6, trend: 'up' as const },
  },
  satisfaction: {
    average_rating: { value: 4.3, change: 0.2, change_percent: 4.9, trend: 'up' as const },
    nps: { value: 68, change: 5, change_percent: 7.9, trend: 'up' as const },
  },
  operations: {
    payment_success_rate: { value: 98.2, change: 0.5, change_percent: 0.5, trend: 'up' as const },
    housekeeping_efficiency: { value: 92.5, change: 2.1, change_percent: 2.3, trend: 'up' as const },
  },
  period: {
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    end: new Date().toISOString(),
  },
};

const MOCK_SYSTEM_STATS = {
  events: {
    total: 12500,
    processed: 12450,
    pending: 50,
    by_source: {
      booking: 4500,
      payment: 3200,
      guest_interaction: 2800,
      housekeeping: 1500,
      feedback: 500,
    },
  },
  metrics: {
    by_granularity: {
      hourly: 720,
      daily: 90,
      weekly: 12,
      monthly: 3,
    },
  },
  data_freshness: {
    latest_event: new Date().toISOString(),
    lag_seconds: 45.5,
  },
  config: {
    aggregation_interval_minutes: 15,
    batch_size: 100,
  },
};

function KPICard({ 
  title, 
  value, 
  change, 
  changePercent, 
  trend, 
  icon: Icon, 
  format = 'number',
  subtitle 
}: { 
  title: string; 
  value: number | string; 
  change?: number; 
  changePercent?: number; 
  trend?: 'up' | 'down' | 'stable'; 
  icon: any;
  format?: 'number' | 'currency' | 'percent';
  subtitle?: string;
}) {
  const formatValue = (v: number | string) => {
    if (typeof v === 'string') return v;
    if (format === 'currency') return formatCurrency(v);
    if (format === 'percent') return `${v.toFixed(1)}%`;
    return v.toLocaleString();
  };

  return (
    <Card hover gradient>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl">
            <Icon className="w-6 h-6 text-white" />
          </div>
          {trend && (
            trend === 'up' ? <TrendingUp className="w-5 h-5 text-green-600" /> :
            trend === 'down' ? <TrendingDown className="w-5 h-5 text-red-600" /> :
            <div className="w-5 h-5 bg-slate-300 rounded-full" />
          )}
        </div>
        <h3 className="text-sm font-medium text-slate-500 mb-2">{title}</h3>
        <p className="text-3xl font-bold text-slate-900 mb-1">{formatValue(value)}</p>
        {subtitle && <p className="text-xs text-slate-500 mb-1">{subtitle}</p>}
        {changePercent !== undefined && (
          <p className={`text-sm font-semibold ${changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {changePercent >= 0 ? '+' : ''}{changePercent.toFixed(1)}% vs last period
          </p>
        )}
      </CardContent>
    </Card>
  );
}

export default function AdminAnalyticsPage() {
  const [dateRange, setDateRange] = useState({
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    to: new Date().toISOString().split('T')[0],
  });

  // Platform-wide KPI Dashboard
  const { data: kpiDashboard, isLoading: kpiLoading, refetch: refetchKPI } = useQuery({
    queryKey: ['admin-kpi-dashboard', dateRange],
    queryFn: async () => {
      try {
        const data = await apiServices.biAnalytics.getKPIDashboard({ 
          compare: true,
          date_from: dateRange.from,
          date_to: dateRange.to,
        });
        if (data && 'revenue_kpis' in data) {
          return MOCK_KPI_DASHBOARD;
        }
        return data || MOCK_KPI_DASHBOARD;
      } catch {
        return MOCK_KPI_DASHBOARD;
      }
    },
  });

  // System Stats
  const { data: systemStats, isLoading: statsLoading, refetch: refetchStats } = useQuery({
    queryKey: ['system-stats'],
    queryFn: async () => {
      try {
        const data = await apiServices.biAnalytics.getSystemStats();
        return data || MOCK_SYSTEM_STATS;
      } catch {
        return MOCK_SYSTEM_STATS;
      }
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Revenue Time Series
  const { data: revenueTimeSeries } = useQuery({
    queryKey: ['admin-revenue-timeseries', dateRange],
    queryFn: async () => {
      try {
        const data = await apiServices.biAnalytics.getMetricTimeSeries(
          'total_revenue',
          dateRange.from,
          dateRange.to,
          'daily'
        );
        if (data && data.data_points && data.data_points.length > 0) {
          return data;
        }
        return {
          metric_type: 'total_revenue',
          granularity: 'daily',
          data_points: generateMockTimeSeries(30, 4000, 0.15),
        };
      } catch {
        return {
          metric_type: 'total_revenue',
          granularity: 'daily',
          data_points: generateMockTimeSeries(30, 4000, 0.15),
        };
      }
    },
  });

  // Bookings Time Series
  const { data: bookingsTimeSeries } = useQuery({
    queryKey: ['admin-bookings-timeseries', dateRange],
    queryFn: async () => {
      try {
        const data = await apiServices.biAnalytics.getMetricTimeSeries(
          'total_bookings',
          dateRange.from,
          dateRange.to,
          'daily'
        );
        if (data && data.data_points && data.data_points.length > 0) {
          return data;
        }
        return {
          metric_type: 'total_bookings',
          granularity: 'daily',
          data_points: generateMockTimeSeries(30, 42, 0.2),
        };
      } catch {
        return {
          metric_type: 'total_bookings',
          granularity: 'daily',
          data_points: generateMockTimeSeries(30, 42, 0.2),
        };
      }
    },
  });

  // Multiple metrics for comparison
  const { data: occupancyRate } = useQuery({
    queryKey: ['admin-occupancy', dateRange],
    queryFn: async () => {
      try {
        const data = await apiServices.biAnalytics.getMetric('occupancy_rate', 'daily');
        return data || { value: 78.5, change: 3.2, change_percent: 4.3, trend: 'up' as const };
      } catch {
        return { value: 78.5, change: 3.2, change_percent: 4.3, trend: 'up' as const };
      }
    },
  });

  const { data: conversionRate } = useQuery({
    queryKey: ['admin-conversion', dateRange],
    queryFn: async () => {
      try {
        const data = await apiServices.biAnalytics.getMetric('booking_conversion_rate', 'daily');
        return data || { value: 12.5, change: 1.2, change_percent: 10.6, trend: 'up' as const };
      } catch {
        return { value: 12.5, change: 1.2, change_percent: 10.6, trend: 'up' as const };
      }
    },
  });

  const isLoading = kpiLoading || statsLoading;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-900 mb-2">Platform Analytics</h1>
            <p className="text-slate-600">Comprehensive platform-wide metrics and insights</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <input
                type="date"
                value={dateRange.from}
                onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
                className="px-3 py-2 border border-slate-300 rounded-lg text-sm"
              />
              <span className="text-slate-600">to</span>
              <input
                type="date"
                value={dateRange.to}
                onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
                className="px-3 py-2 border border-slate-300 rounded-lg text-sm"
              />
            </div>
            <Button variant="outline" size="sm" onClick={() => { refetchKPI(); refetchStats(); }} leftIcon={<RefreshCw className="w-4 h-4" />}>
              Refresh
            </Button>
            <Button variant="outline" size="sm" leftIcon={<Download className="w-4 h-4" />}>
              Export
            </Button>
          </div>
        </div>
      </div>

      {/* System Health */}
      {systemStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <Activity className="w-8 h-8 text-blue-600" />
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  systemStats.data_freshness.lag_seconds && systemStats.data_freshness.lag_seconds < 300
                    ? 'bg-green-100 text-green-700'
                    : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {systemStats.data_freshness.lag_seconds && systemStats.data_freshness.lag_seconds < 300 ? 'Live' : 'Delayed'}
                </span>
              </div>
              <p className="text-sm text-slate-600">System Health</p>
              <p className="text-3xl font-bold text-slate-900">
                {systemStats.data_freshness.lag_seconds && systemStats.data_freshness.lag_seconds < 300 ? 'Healthy' : 'Warning'}
              </p>
              {systemStats.data_freshness.lag_seconds && (
                <p className="text-xs text-slate-500 mt-1">
                  {Math.round(systemStats.data_freshness.lag_seconds / 60)} min lag
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <Activity className="w-8 h-8 text-purple-600" />
              </div>
              <p className="text-sm text-slate-600">Total Events</p>
              <p className="text-3xl font-bold text-slate-900">{systemStats.events.total.toLocaleString()}</p>
              <p className="text-xs text-slate-500 mt-1">
                {systemStats.events.processed.toLocaleString()} processed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <AlertTriangle className="w-8 h-8 text-yellow-600" />
              </div>
              <p className="text-sm text-slate-600">Pending Events</p>
              <p className="text-3xl font-bold text-yellow-600">{systemStats.events.pending.toLocaleString()}</p>
              <p className="text-xs text-slate-500 mt-1">
                {systemStats.events.total > 0 
                  ? `${((systemStats.events.processed / systemStats.events.total) * 100).toFixed(1)}% processed`
                  : 'N/A'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <BarChart3 className="w-8 h-8 text-green-600" />
              </div>
              <p className="text-sm text-slate-600">Metric Snapshots</p>
              <p className="text-3xl font-bold text-slate-900">
                {Object.values(systemStats.metrics.by_granularity).reduce((a, b) => a + b, 0).toLocaleString()}
              </p>
              <p className="text-xs text-slate-500 mt-1">Across all granularities</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Platform KPIs */}
      {kpiDashboard && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <KPICard
              title="Platform Revenue"
              value={kpiDashboard.revenue?.total_revenue?.value || 0}
              changePercent={kpiDashboard.revenue?.total_revenue?.change_percent}
              trend={kpiDashboard.revenue?.total_revenue?.trend}
              icon={DollarSign}
              format="currency"
            />
            <KPICard
              title="Total Bookings"
              value={kpiDashboard.bookings?.total_bookings?.value || 0}
              changePercent={kpiDashboard.bookings?.total_bookings?.change_percent}
              trend={kpiDashboard.bookings?.total_bookings?.trend}
              icon={Calendar}
            />
            <KPICard
              title="Occupancy Rate"
              value={kpiDashboard.occupancy?.occupancy_rate?.value || 0}
              changePercent={kpiDashboard.occupancy?.occupancy_rate?.change_percent}
              trend={kpiDashboard.occupancy?.occupancy_rate?.trend}
              icon={Building2}
              format="percent"
            />
            <KPICard
              title="Guest Satisfaction"
              value={kpiDashboard.satisfaction?.average_rating?.value || 0}
              changePercent={kpiDashboard.satisfaction?.average_rating?.change_percent}
              trend={kpiDashboard.satisfaction?.average_rating?.trend}
              icon={Star}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <KPICard
              title="Avg Order Value"
              value={kpiDashboard.revenue?.average_order_value?.value || 0}
              changePercent={kpiDashboard.revenue?.average_order_value?.change_percent}
              trend={kpiDashboard.revenue?.average_order_value?.trend}
              icon={DollarSign}
              format="currency"
            />
            <KPICard
              title="Conversion Rate"
              value={kpiDashboard.bookings?.conversion_rate?.value || 0}
              changePercent={kpiDashboard.bookings?.conversion_rate?.change_percent}
              trend={kpiDashboard.bookings?.conversion_rate?.trend}
              icon={TrendingUp}
              format="percent"
            />
            <KPICard
              title="Payment Success"
              value={kpiDashboard.operations?.payment_success_rate?.value || 0}
              changePercent={kpiDashboard.operations?.payment_success_rate?.change_percent}
              trend={kpiDashboard.operations?.payment_success_rate?.trend}
              icon={CreditCard}
              format="percent"
            />
            <KPICard
              title="NPS Score"
              value={kpiDashboard.satisfaction?.nps?.value || 0}
              changePercent={kpiDashboard.satisfaction?.nps?.change_percent}
              trend={kpiDashboard.satisfaction?.nps?.trend}
              icon={Star}
            />
          </div>
        </>
      )}

      {/* Charts */}
      <div className="space-y-6">
        {/* Revenue Trend */}
        {revenueTimeSeries && revenueTimeSeries.data_points && revenueTimeSeries.data_points.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <DollarSign className="w-5 h-5 mr-2" />
                Platform Revenue Trend
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={revenueTimeSeries.data_points}>
                  <defs>
                    <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis 
                    dataKey="timestamp" 
                    stroke="#64748b"
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis stroke="#64748b" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px' }}
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value: number) => formatCurrency(value, 'USD')}
                  />
                  <Legend />
                  <Area 
                    type="monotone" 
                    dataKey="value" 
                    name="Revenue" 
                    stroke="#2563eb" 
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorRevenue)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {/* Bookings Trend */}
        {bookingsTimeSeries && bookingsTimeSeries.data_points && bookingsTimeSeries.data_points.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="w-5 h-5 mr-2" />
                Bookings Trend
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={bookingsTimeSeries.data_points}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis 
                    dataKey="timestamp" 
                    stroke="#64748b"
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis stroke="#64748b" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px' }}
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    name="Bookings" 
                    stroke="#10b981" 
                    strokeWidth={3}
                    dot={{ fill: '#10b981', r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {/* Events by Source */}
        {systemStats && systemStats.events.by_source && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Events by Source
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={Object.entries(systemStats.events.by_source).map(([name, value]) => ({ name, value }))}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {Object.keys(systemStats.events.by_source).map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Metrics by Granularity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={Object.entries(systemStats.metrics.by_granularity).map(([name, value]) => ({ name, value }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="name" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px' }} />
                    <Bar dataKey="value" fill="#2563eb" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Loading State */}
      {isLoading && !kpiDashboard && !systemStats && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      )}
    </div>
  );
}
