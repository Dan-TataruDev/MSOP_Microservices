import { useQuery } from '@tanstack/react-query';
import { TrendingUp, DollarSign, Calendar, Package, BarChart3 } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { formatCurrency, formatPercentage } from '@hospitality-platform/utils';
import type { BusinessMetrics } from '@hospitality-platform/types';

export default function DashboardPage() {
  const { businessContext } = useAuthStore();
  const businessId = businessContext?.businessId || 'demo';

  const { data: metrics, isLoading } = useQuery<BusinessMetrics>({
    queryKey: ['metrics', businessId],
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
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Dashboard</h1>
        <p className="text-slate-600">Overview of your business performance</p>
      </div>
      
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card hover gradient>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-blue-100 rounded-xl">
                  <DollarSign className="w-6 h-6 text-blue-600" />
                </div>
                <TrendingUp className={`w-5 h-5 ${metrics.revenue.change >= 0 ? 'text-green-600' : 'text-red-600'}`} />
              </div>
              <h3 className="text-sm font-medium text-slate-500 mb-2">Total Revenue</h3>
              <p className="text-3xl font-bold text-slate-900 mb-1">{formatCurrency(metrics.revenue.total)}</p>
              <p className={`text-sm font-semibold ${metrics.revenue.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {metrics.revenue.change >= 0 ? '+' : ''}{formatPercentage(metrics.revenue.changePercent)}
              </p>
            </CardContent>
          </Card>
          
          <Card hover gradient>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-purple-100 rounded-xl">
                  <Calendar className="w-6 h-6 text-purple-600" />
                </div>
              </div>
              <h3 className="text-sm font-medium text-slate-500 mb-2">Total Bookings</h3>
              <p className="text-3xl font-bold text-slate-900 mb-1">{metrics.bookings.total}</p>
              <p className="text-sm text-slate-600">
                {metrics.bookings.confirmed} confirmed
              </p>
            </CardContent>
          </Card>
          
          <Card hover gradient>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-green-100 rounded-xl">
                  <Package className="w-6 h-6 text-green-600" />
                </div>
              </div>
              <h3 className="text-sm font-medium text-slate-500 mb-2">Total Orders</h3>
              <p className="text-3xl font-bold text-slate-900 mb-1">{metrics.orders.total}</p>
              <p className="text-sm text-slate-600">
                Avg: {formatCurrency(metrics.orders.averageOrderValue)}
              </p>
            </CardContent>
          </Card>
          
          <Card hover gradient>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-orange-100 rounded-xl">
                  <BarChart3 className="w-6 h-6 text-orange-600" />
                </div>
              </div>
              <h3 className="text-sm font-medium text-slate-500 mb-2">Sentiment Score</h3>
              <p className="text-3xl font-bold text-slate-900 mb-1">{metrics.sentiment.averageScore.toFixed(1)}</p>
              <p className={`text-sm font-semibold ${
                metrics.sentiment.trend === 'improving' ? 'text-green-600' :
                metrics.sentiment.trend === 'declining' ? 'text-red-600' :
                'text-slate-600'
              }`}>
                {metrics.sentiment.trend}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card hover className="cursor-pointer" onClick={() => window.location.href = '/business/inventory'}>
              <CardContent className="p-6">
                <h3 className="font-semibold text-slate-900 mb-2">Manage Inventory</h3>
                <p className="text-sm text-slate-600">Update stock levels and view alerts</p>
              </CardContent>
            </Card>
            <Card hover className="cursor-pointer" onClick={() => window.location.href = '/business/bookings'}>
              <CardContent className="p-6">
                <h3 className="font-semibold text-slate-900 mb-2">View Bookings</h3>
                <p className="text-sm text-slate-600">Check upcoming reservations</p>
              </CardContent>
            </Card>
            <Card hover className="cursor-pointer" onClick={() => window.location.href = '/business/analytics'}>
              <CardContent className="p-6">
                <h3 className="font-semibold text-slate-900 mb-2">Analytics</h3>
                <p className="text-sm text-slate-600">View detailed reports and insights</p>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

