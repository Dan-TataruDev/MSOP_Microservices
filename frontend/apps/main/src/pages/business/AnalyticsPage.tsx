import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';
import { BarChart3, DollarSign, Calendar, TrendingUp, TrendingDown, Users, Star, Clock, CheckCircle, Filter, Download } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { formatCurrency, formatPercentage } from '@hospitality-platform/utils';
import type { BusinessMetrics } from '@hospitality-platform/types';

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

function KPICard({ 
  title, 
  value, 
  change, 
  changePercent, 
  trend, 
  icon: Icon, 
  format = 'number' 
}: { 
  title: string; 
  value: number; 
  change?: number; 
  changePercent?: number; 
  trend?: 'up' | 'down' | 'stable'; 
  icon: any;
  format?: 'number' | 'currency' | 'percent';
}) {
  const formatValue = (v: number) => {
    if (format === 'currency') return formatCurrency(v);
    if (format === 'percent') return `${v.toFixed(1)}%`;
    return v.toLocaleString();
  };

  return (
    <Card hover gradient>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="p-3 bg-blue-100 rounded-xl">
            <Icon className="w-6 h-6 text-blue-600" />
          </div>
          {trend && (
            trend === 'up' ? <TrendingUp className="w-5 h-5 text-green-600" /> :
            trend === 'down' ? <TrendingDown className="w-5 h-5 text-red-600" /> :
            <div className="w-5 h-5 bg-slate-300 rounded-full" />
          )}
        </div>
        <h3 className="text-sm font-medium text-slate-500 mb-2">{title}</h3>
        <p className="text-3xl font-bold text-slate-900 mb-1">{formatValue(value)}</p>
        {changePercent !== undefined && (
          <p className={`text-sm font-semibold ${changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {changePercent >= 0 ? '+' : ''}{changePercent.toFixed(1)}% vs last period
          </p>
        )}
      </CardContent>
    </Card>
  );
}

export default function AnalyticsPage() {
  const { businessContext } = useAuthStore();
  const businessId = businessContext?.businessId || 'demo';
  const [dateRange, setDateRange] = useState({
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    to: new Date().toISOString().split('T')[0],
  });

  // Fetch KPI Dashboard from bi-analytics service
  const { data: kpiDashboard, isLoading: kpiLoading } = useQuery({
    queryKey: ['kpi-dashboard', dateRange],
    queryFn: async () => {
      try {
        return await apiServices.biAnalytics.getKPIDashboard({ 
          compare: true,
          date_from: dateRange.from,
          date_to: dateRange.to,
        });
      } catch {
        return null;
      }
    },
  });

  // Fetch Revenue Dashboard
  const { data: revenueDashboard } = useQuery({
    queryKey: ['revenue-dashboard', dateRange],
    queryFn: async () => {
      try {
        return await apiServices.biAnalytics.getRevenueDashboard({
          date_from: dateRange.from,
          date_to: dateRange.to,
        });
      } catch {
        return null;
      }
    },
  });

  // Fetch Operations Dashboard
  const { data: operationsDashboard } = useQuery({
    queryKey: ['operations-dashboard', dateRange],
    queryFn: async () => {
      try {
        return await apiServices.biAnalytics.getOperationsDashboard({
          date_from: dateRange.from,
          date_to: dateRange.to,
        });
      } catch {
        return null;
      }
    },
  });

  // Fetch time series data for revenue
  const { data: revenueTimeSeries } = useQuery({
    queryKey: ['revenue-timeseries', dateRange],
    queryFn: async () => {
      try {
        return await apiServices.biAnalytics.getMetricTimeSeries(
          'total_revenue',
          dateRange.from,
          dateRange.to,
          'daily'
        );
      } catch {
        return null;
      }
    },
  });

  // Fetch existing business metrics for charts
  const { data: metrics, isLoading: metricsLoading } = useQuery<BusinessMetrics>({
    queryKey: ['analytics', businessId],
    queryFn: async () => {
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 30);
      const response = await apiServices.analytics.getBusinessMetrics(businessId, {
        start: startDate.toISOString(),
        end: endDate.toISOString(),
      });
      return response.data;
    },
    enabled: !!businessId,
  });

  const isLoading = kpiLoading || metricsLoading;

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Analytics Dashboard</h1>
        <p className="text-slate-600">Comprehensive business insights and KPIs</p>
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
            <Button variant="outline" size="sm" leftIcon={<Download className="w-4 h-4" />}>
              Export
            </Button>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      {kpiDashboard && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <KPICard
            title="Total Revenue"
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
            icon={Users}
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
      )}

      {/* Secondary KPIs */}
      {kpiDashboard && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
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
            icon={CheckCircle}
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
      )}

      {/* Revenue Time Series Chart */}
      {revenueTimeSeries && revenueTimeSeries.data_points && revenueTimeSeries.data_points.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="w-5 h-5 mr-2" />
              Revenue Trend (Time Series)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
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

      {/* Revenue Dashboard Details */}
      {revenueDashboard && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <DollarSign className="w-5 h-5 mr-2" />
              Revenue Analytics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(revenueDashboard.metrics || {}).map(([key, metric]: [string, any]) => (
                <div key={key} className="p-4 bg-slate-50 rounded-lg">
                  <p className="text-sm text-slate-600 mb-1 capitalize">{key.replace(/_/g, ' ')}</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {key.includes('revenue') || key.includes('value') 
                      ? formatCurrency(metric.value, 'USD')
                      : `${metric.value.toFixed(1)}%`}
                  </p>
                  {metric.change_percent !== undefined && (
                    <p className={`text-sm mt-1 ${metric.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {metric.change_percent >= 0 ? '+' : ''}{metric.change_percent.toFixed(1)}%
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Charts */}
      {metrics && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Revenue Trend
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={metrics.revenue.byPeriod}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="date" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px' }} />
                  <Legend />
                  <Line type="monotone" dataKey="value" name="Revenue" stroke="#2563eb" strokeWidth={2} dot={{ fill: '#2563eb' }} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Bookings by Day</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={metrics.bookings.byPeriod}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="date" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px' }} />
                    <Bar dataKey="value" name="Bookings" fill="#2563eb" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Orders by Day</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={metrics.orders.byPeriod}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="date" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px' }} />
                    <Bar dataKey="value" name="Orders" fill="#10b981" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Fallback if no data */}
      {!kpiDashboard && !metrics && (
        <Card>
          <CardContent className="p-12 text-center">
            <BarChart3 className="w-12 h-12 text-slate-200 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 mb-2">No Analytics Data</h3>
            <p className="text-slate-600">Analytics data will appear here once you start receiving bookings and orders.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

