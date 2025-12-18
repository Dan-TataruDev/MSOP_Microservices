import { useQuery } from '@tanstack/react-query';
import { apiServices, useAuthStore } from '../stores/authStore';
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
      <div className="container mx-auto px-4">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Total Revenue</h3>
            <p className="text-2xl font-bold">{formatCurrency(metrics.revenue.total)}</p>
            <p className={`text-sm mt-1 ${metrics.revenue.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {metrics.revenue.change >= 0 ? '+' : ''}{formatPercentage(metrics.revenue.changePercent)}
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Total Bookings</h3>
            <p className="text-2xl font-bold">{metrics.bookings.total}</p>
            <p className="text-sm text-gray-600 mt-1">
              {metrics.bookings.confirmed} confirmed
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Total Orders</h3>
            <p className="text-2xl font-bold">{metrics.orders.total}</p>
            <p className="text-sm text-gray-600 mt-1">
              Avg: {formatCurrency(metrics.orders.averageOrderValue)}
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Sentiment Score</h3>
            <p className="text-2xl font-bold">{metrics.sentiment.averageScore.toFixed(1)}</p>
            <p className={`text-sm mt-1 ${
              metrics.sentiment.trend === 'improving' ? 'text-green-600' :
              metrics.sentiment.trend === 'declining' ? 'text-red-600' :
              'text-gray-600'
            }`}>
              {metrics.sentiment.trend}
            </p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
            <h3 className="font-medium mb-2">Manage Inventory</h3>
            <p className="text-sm text-gray-600">Update stock levels and view alerts</p>
          </div>
          <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
            <h3 className="font-medium mb-2">View Bookings</h3>
            <p className="text-sm text-gray-600">Check upcoming reservations</p>
          </div>
          <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
            <h3 className="font-medium mb-2">Analytics</h3>
            <p className="text-sm text-gray-600">View detailed reports and insights</p>
          </div>
        </div>
      </div>
    </div>
  );
}

