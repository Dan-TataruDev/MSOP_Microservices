import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Calendar, Clock, MapPin, Users, DollarSign, Filter, CheckCircle, XCircle, Clock as ClockIcon } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { formatDate, formatDateTime, formatCurrency } from '@hospitality-platform/utils';

type StatusFilter = 'all' | 'pending' | 'confirmed' | 'checked_in' | 'completed' | 'cancelled';

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-700',
  confirmed: 'bg-green-100 text-green-700',
  checked_in: 'bg-blue-100 text-blue-700',
  completed: 'bg-purple-100 text-purple-700',
  cancelled: 'bg-red-100 text-red-700',
};

const statusIcons: Record<string, any> = {
  confirmed: CheckCircle,
  completed: CheckCircle,
  cancelled: XCircle,
  pending: ClockIcon,
  checked_in: ClockIcon,
};

export default function BookingHistoryPage() {
  const { user } = useAuthStore();
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [page, setPage] = useState(1);

  // Get bookings
  const { data: bookingsData, isLoading } = useQuery({
    queryKey: ['user-bookings', statusFilter, page],
    queryFn: async () => {
      const response = await apiServices.bookings.getUserBookings();
      return response.data;
    },
    enabled: !!user,
  });

  const bookings = Array.isArray(bookingsData) ? bookingsData : (bookingsData?.items || []);

  // Filter bookings by status
  const filteredBookings = bookings.filter((booking: any) => {
    if (statusFilter === 'all') return true;
    return booking.status === statusFilter;
  });

  // Get payment for each booking
  const getBookingPayment = async (bookingId: string) => {
    try {
      const response = await apiServices.payments.getOrderPayment(bookingId);
      return response.data;
    } catch {
      return null;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Booking History</h1>
        <p className="text-slate-600">View and manage all your bookings</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <Calendar className="w-8 h-8 text-blue-600" />
            </div>
            <p className="text-sm text-slate-600">Total Bookings</p>
            <p className="text-3xl font-bold text-slate-900">{bookings.length}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <p className="text-sm text-slate-600">Confirmed</p>
            <p className="text-3xl font-bold text-green-600">
              {bookings.filter((b: any) => b.status === 'confirmed').length}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <ClockIcon className="w-8 h-8 text-yellow-600" />
            </div>
            <p className="text-sm text-slate-600">Pending</p>
            <p className="text-3xl font-bold text-yellow-600">
              {bookings.filter((b: any) => b.status === 'pending').length}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <XCircle className="w-8 h-8 text-red-600" />
            </div>
            <p className="text-sm text-slate-600">Cancelled</p>
            <p className="text-3xl font-bold text-red-600">
              {bookings.filter((b: any) => b.status === 'cancelled').length}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-500" />
              <span className="text-sm font-medium text-slate-700">Status:</span>
            </div>
            <div className="flex gap-2">
              {(['all', 'pending', 'confirmed', 'checked_in', 'completed', 'cancelled'] as StatusFilter[]).map((status) => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors capitalize ${
                    statusFilter === status
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  {status}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Bookings List */}
      <Card>
        <CardHeader>
          <CardTitle>My Bookings</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : filteredBookings.length > 0 ? (
            <div className="space-y-4">
              {filteredBookings.map((booking: any) => {
                const StatusIcon = statusIcons[booking.status] || ClockIcon;
                return (
                  <div key={booking.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <h4 className="text-lg font-semibold text-slate-900">
                            {booking.venueName || booking.venue_name || 'Venue'}
                          </h4>
                          <span className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1 ${statusColors[booking.status] || 'bg-slate-100 text-slate-700'}`}>
                            <StatusIcon className="w-3 h-3" />
                            {booking.status}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-3">
                          <div className="flex items-center gap-2 text-sm">
                            <Calendar className="w-4 h-4 text-slate-500" />
                            <div>
                              <p className="text-slate-600">Date</p>
                              <p className="font-semibold text-slate-900">
                                {booking.date ? formatDate(booking.date) : formatDate(booking.booking_date || booking.created_at)}
                              </p>
                            </div>
                          </div>
                          
                          <div className="flex items-center gap-2 text-sm">
                            <Clock className="w-4 h-4 text-slate-500" />
                            <div>
                              <p className="text-slate-600">Time</p>
                              <p className="font-semibold text-slate-900">
                                {booking.time || booking.booking_time || 'N/A'}
                              </p>
                            </div>
                          </div>
                          
                          <div className="flex items-center gap-2 text-sm">
                            <Users className="w-4 h-4 text-slate-500" />
                            <div>
                              <p className="text-slate-600">Party Size</p>
                              <p className="font-semibold text-slate-900">
                                {booking.partySize || booking.party_size || 'N/A'}
                              </p>
                            </div>
                          </div>
                          
                          {booking.total_amount && (
                            <div className="flex items-center gap-2 text-sm">
                              <DollarSign className="w-4 h-4 text-slate-500" />
                              <div>
                                <p className="text-slate-600">Amount</p>
                                <p className="font-semibold text-slate-900">
                                  {formatCurrency(booking.total_amount, booking.currency || 'USD')}
                                </p>
                              </div>
                            </div>
                          )}
                        </div>

                        {booking.venue_address && (
                          <div className="flex items-start gap-2 text-sm text-slate-600 mt-2">
                            <MapPin className="w-4 h-4 mt-0.5" />
                            <span>{booking.venue_address}</span>
                          </div>
                        )}

                        {booking.booking_reference && (
                          <div className="mt-2">
                            <span className="text-xs text-slate-500">Reference: </span>
                            <span className="text-xs font-mono text-slate-700">{booking.booking_reference}</span>
                          </div>
                        )}

                        {booking.special_requests && (
                          <div className="mt-3 p-2 bg-blue-50 border border-blue-200 rounded text-sm">
                            <p className="font-medium text-blue-900 mb-1">Special Requests:</p>
                            <p className="text-blue-700">{booking.special_requests}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-12">
              <Calendar className="w-12 h-12 text-slate-200 mx-auto mb-3" />
              <p className="text-slate-500">No bookings found</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
