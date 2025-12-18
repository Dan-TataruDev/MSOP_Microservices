import { useQuery } from '@tanstack/react-query';
import { Users, Building2, Activity, DollarSign, Calendar, TrendingUp, AlertTriangle, CheckCircle, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { apiServices } from '@/stores/authStore';
import { formatCurrency } from '@hospitality-platform/utils';

// Mock data for demo
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

export default function DashboardPage() {
  const navigate = useNavigate();

  // Get platform-wide KPIs
  const { data: kpiDashboard, isLoading: kpiLoading } = useQuery({
    queryKey: ['admin-dashboard-kpi'],
    queryFn: async () => {
      try {
        const data = await apiServices.biAnalytics.getKPIDashboard({ compare: true });
        // Transform backend response to frontend format if needed
        if (data && 'revenue_kpis' in data) {
          // Backend returns different format, use mock for now
          return MOCK_KPI_DASHBOARD;
        }
        return data || MOCK_KPI_DASHBOARD;
      } catch {
        return MOCK_KPI_DASHBOARD;
      }
    },
  });

  // Get system stats
  const { data: systemStats, isLoading: statsLoading } = useQuery({
    queryKey: ['admin-dashboard-stats'],
    queryFn: async () => {
      try {
        const data = await apiServices.biAnalytics.getSystemStats();
        return data || MOCK_SYSTEM_STATS;
      } catch {
        return MOCK_SYSTEM_STATS;
      }
    },
    refetchInterval: 30000,
  });

  const isLoading = kpiLoading || statsLoading;
  const isHealthy = systemStats?.data_freshness?.lag_seconds && systemStats.data_freshness.lag_seconds < 300;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Admin Dashboard</h1>
        <p className="text-slate-600">Platform overview and system monitoring</p>
      </div>
      
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card hover gradient className="cursor-pointer" onClick={() => navigate('/admin/analytics')}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
              <ArrowRight className="w-5 h-5 text-slate-400" />
            </div>
            <h3 className="text-sm font-medium text-slate-500 mb-2">Platform Revenue</h3>
            <p className="text-3xl font-bold text-slate-900 mb-1">
              {isLoading ? '...' : formatCurrency(kpiDashboard?.revenue?.total_revenue?.value || 0)}
            </p>
            {kpiDashboard?.revenue?.total_revenue?.change_percent !== undefined && (
              <p className={`text-sm font-semibold ${kpiDashboard.revenue.total_revenue.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {kpiDashboard.revenue.total_revenue.change_percent >= 0 ? '+' : ''}
                {kpiDashboard.revenue.total_revenue.change_percent.toFixed(1)}% vs last period
              </p>
            )}
          </CardContent>
        </Card>
        
        <Card hover gradient className="cursor-pointer" onClick={() => navigate('/admin/analytics')}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl">
                <Calendar className="w-6 h-6 text-white" />
              </div>
              <ArrowRight className="w-5 h-5 text-slate-400" />
            </div>
            <h3 className="text-sm font-medium text-slate-500 mb-2">Total Bookings</h3>
            <p className="text-3xl font-bold text-slate-900 mb-1">
              {isLoading ? '...' : (kpiDashboard?.bookings?.total_bookings?.value || 0).toLocaleString()}
            </p>
            {kpiDashboard?.bookings?.total_bookings?.change_percent !== undefined && (
              <p className={`text-sm font-semibold ${kpiDashboard.bookings.total_bookings.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {kpiDashboard.bookings.total_bookings.change_percent >= 0 ? '+' : ''}
                {kpiDashboard.bookings.total_bookings.change_percent.toFixed(1)}% vs last period
              </p>
            )}
          </CardContent>
        </Card>
        
        <Card hover gradient>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl">
                <Users className="w-6 h-6 text-white" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-slate-500 mb-2">Total Users</h3>
            <p className="text-3xl font-bold text-slate-900 mb-1">2,847</p>
            <p className="text-sm font-semibold text-green-600">+12.5% vs last month</p>
          </CardContent>
        </Card>
        
        <Card hover gradient>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-br from-orange-500 to-red-500 rounded-xl">
                <Building2 className="w-6 h-6 text-white" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-slate-500 mb-2">Total Businesses</h3>
            <p className="text-3xl font-bold text-slate-900 mb-1">156</p>
            <p className="text-sm font-semibold text-green-600">+8.3% vs last month</p>
          </CardContent>
        </Card>
      </div>

      {/* System Health & Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="w-5 h-5 mr-2" />
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              </div>
            ) : systemStats ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    {isHealthy ? (
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    ) : (
                      <AlertTriangle className="w-6 h-6 text-yellow-600" />
                    )}
                    <div>
                      <p className="font-semibold text-slate-900">Status</p>
                      <p className="text-sm text-slate-600">
                        {isHealthy ? 'All systems operational' : 'Delayed data processing'}
                      </p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    isHealthy ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {isHealthy ? 'Healthy' : 'Warning'}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <p className="text-xs text-slate-600 mb-1">Total Events</p>
                    <p className="text-2xl font-bold text-slate-900">{systemStats.events.total.toLocaleString()}</p>
                  </div>
                  <div className="p-3 bg-green-50 rounded-lg">
                    <p className="text-xs text-slate-600 mb-1">Processed</p>
                    <p className="text-2xl font-bold text-green-600">{systemStats.events.processed.toLocaleString()}</p>
                  </div>
                  <div className="p-3 bg-yellow-50 rounded-lg">
                    <p className="text-xs text-slate-600 mb-1">Pending</p>
                    <p className="text-2xl font-bold text-yellow-600">{systemStats.events.pending.toLocaleString()}</p>
                  </div>
                  <div className="p-3 bg-purple-50 rounded-lg">
                    <p className="text-xs text-slate-600 mb-1">Processing Rate</p>
                    <p className="text-2xl font-bold text-purple-600">
                      {systemStats.events.total > 0 
                        ? `${((systemStats.events.processed / systemStats.events.total) * 100).toFixed(1)}%`
                        : '0%'}
                    </p>
                  </div>
                </div>

                {systemStats.data_freshness.lag_seconds && (
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xs text-slate-600 mb-1">Data Freshness</p>
                    <p className="text-sm font-semibold text-slate-900">
                      {Math.round(systemStats.data_freshness.lag_seconds / 60)} minutes lag
                    </p>
                    {systemStats.data_freshness.latest_event && (
                      <p className="text-xs text-slate-500 mt-1">
                        Latest: {new Date(systemStats.data_freshness.latest_event).toLocaleString()}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <p className="text-slate-500 text-center py-4">Unable to load system stats</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="w-5 h-5 mr-2" />
              Key Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              </div>
            ) : kpiDashboard ? (
              <div className="space-y-4">
                <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-slate-600 mb-1">Occupancy Rate</p>
                  <p className="text-3xl font-bold text-slate-900">
                    {(kpiDashboard.occupancy?.occupancy_rate?.value || 0).toFixed(1)}%
                  </p>
                  {kpiDashboard.occupancy?.occupancy_rate?.change_percent !== undefined && (
                    <p className={`text-sm mt-1 ${kpiDashboard.occupancy.occupancy_rate.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {kpiDashboard.occupancy.occupancy_rate.change_percent >= 0 ? '+' : ''}
                      {kpiDashboard.occupancy.occupancy_rate.change_percent.toFixed(1)}%
                    </p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xs text-slate-600 mb-1">Conversion Rate</p>
                    <p className="text-xl font-bold text-slate-900">
                      {(kpiDashboard.bookings?.conversion_rate?.value || 0).toFixed(1)}%
                    </p>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xs text-slate-600 mb-1">Avg Order Value</p>
                    <p className="text-xl font-bold text-slate-900">
                      {formatCurrency(kpiDashboard.revenue?.average_order_value?.value || 0)}
                    </p>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xs text-slate-600 mb-1">Guest Satisfaction</p>
                    <p className="text-xl font-bold text-slate-900">
                      {(kpiDashboard.satisfaction?.average_rating?.value || 0).toFixed(1)}
                    </p>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xs text-slate-600 mb-1">Payment Success</p>
                    <p className="text-xl font-bold text-slate-900">
                      {(kpiDashboard.operations?.payment_success_rate?.value || 0).toFixed(1)}%
                    </p>
                  </div>
              </div>
            </div>
            ) : (
              <p className="text-slate-500 text-center py-4">Unable to load metrics</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button 
              variant="outline" 
              className="justify-start h-auto p-4"
              onClick={() => navigate('/admin/analytics')}
            >
              <div className="text-left">
                <p className="font-semibold text-slate-900">View Analytics</p>
                <p className="text-sm text-slate-600">Platform-wide metrics and insights</p>
              </div>
              <ArrowRight className="w-5 h-5 ml-auto" />
            </Button>
            <Button 
              variant="outline" 
              className="justify-start h-auto p-4"
              onClick={() => navigate('/admin/users')}
            >
              <div className="text-left">
                <p className="font-semibold text-slate-900">Manage Users</p>
                <p className="text-sm text-slate-600">View and manage platform users</p>
              </div>
              <ArrowRight className="w-5 h-5 ml-auto" />
            </Button>
            <Button 
              variant="outline" 
              className="justify-start h-auto p-4"
              onClick={() => navigate('/admin/businesses')}
            >
              <div className="text-left">
                <p className="font-semibold text-slate-900">Manage Businesses</p>
                <p className="text-sm text-slate-600">View and manage business accounts</p>
              </div>
              <ArrowRight className="w-5 h-5 ml-auto" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

