import { useQuery } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { apiServices, useAuthStore } from '../stores/authStore';
import { formatDate, formatDateTime } from '@hospitality-platform/utils';

export default function ProfilePage() {
  const { user } = useAuthStore();

  const { data: bookings } = useQuery({
    queryKey: ['bookings', 'me'],
    queryFn: async () => {
      const response = await apiServices.bookings.getUserBookings();
      return response.data;
    },
    enabled: !!user,
  });

  const { data: orders } = useQuery({
    queryKey: ['orders', 'me'],
    queryFn: async () => {
      const response = await apiServices.orders.getUserOrders();
      return response.data;
    },
    enabled: !!user,
  });

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">My Profile</h1>
        
        {user && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Account Information</h2>
            <div className="space-y-2">
              <p><span className="font-medium">Name:</span> {user.name}</p>
              <p><span className="font-medium">Email:</span> {user.email}</p>
              {user.phone && <p><span className="font-medium">Phone:</span> {user.phone}</p>}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">My Bookings</h2>
            {bookings && bookings.length > 0 ? (
              <div className="space-y-4">
                {bookings.map((booking) => (
                  <div key={booking.id} className="border-b pb-4 last:border-b-0">
                    <h3 className="font-semibold">{booking.venueName}</h3>
                    <p className="text-sm text-gray-600">
                      {formatDate(booking.date)} at {booking.time}
                    </p>
                    <p className="text-sm text-gray-600">Party size: {booking.partySize}</p>
                    <span className={`inline-block mt-2 px-2 py-1 rounded text-xs ${
                      booking.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                      booking.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {booking.status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No bookings yet</p>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">My Orders</h2>
            {orders && orders.length > 0 ? (
              <div className="space-y-4">
                {orders.map((order) => (
                  <div key={order.id} className="border-b pb-4 last:border-b-0">
                    <h3 className="font-semibold">{order.venueName}</h3>
                    <p className="text-sm text-gray-600">
                      {formatDateTime(order.createdAt)}
                    </p>
                    <p className="text-sm text-gray-600">
                      Total: {formatCurrency(order.total)}
                    </p>
                    <span className={`inline-block mt-2 px-2 py-1 rounded text-xs ${
                      order.status === 'delivered' ? 'bg-green-100 text-green-800' :
                      order.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {order.status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No orders yet</p>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}

