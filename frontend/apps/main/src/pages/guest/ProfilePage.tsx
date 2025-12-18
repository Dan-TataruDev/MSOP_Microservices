import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Calendar, Package, User, Settings, Heart, Trophy, ArrowRight, CreditCard, BookOpen, History } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { formatDate, formatDateTime, formatCurrency } from '@hospitality-platform/utils';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();

  const { data: loyaltyMember } = useQuery({
    queryKey: ['loyalty-member', user?.id],
    queryFn: async () => {
      if (!user?.id) return null;
      try {
        return await apiServices.loyalty.getMemberStatus(user.id);
      } catch {
        return null;
      }
    },
    enabled: !!user?.id,
  });

  const { data: favorites } = useQuery({
    queryKey: ['favorites-count'],
    queryFn: async () => {
      try {
        return await apiServices.favorites.listFavorites(1, 1);
      } catch {
        return { total: 0 };
      }
    },
    enabled: !!user,
  });

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

  // Get guest profile from personalization service
  const { data: guestProfile } = useQuery({
    queryKey: ['guest-profile', user?.id],
    queryFn: async () => {
      if (!user?.id) return null;
      try {
        const response = await apiServices.personalization.getGuestProfile(user.id);
        return response.data;
      } catch (error) {
        // If guest profile doesn't exist, return null
        return null;
      }
    },
    enabled: !!user?.id,
  });

  // Get preferences
  const { data: preferences } = useQuery({
    queryKey: ['guest-preferences', user?.id],
    queryFn: async () => {
      if (!user?.id) return [];
      try {
        const response = await apiServices.personalization.getGuestPreferences(user.id);
        return response.data;
      } catch (error) {
        return [];
      }
    },
    enabled: !!user?.id && !!guestProfile,
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-slate-900">My Profile</h1>
      
      {user && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="w-5 h-5 mr-2" />
              Account Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <span className="font-semibold text-slate-700">Name:</span>
                <span className="ml-2 text-slate-900">{user.name}</span>
              </div>
              <div>
                <span className="font-semibold text-slate-700">Email:</span>
                <span className="ml-2 text-slate-900">{user.email}</span>
              </div>
              {user.phone && (
                <div>
                  <span className="font-semibold text-slate-700">Phone:</span>
                  <span className="ml-2 text-slate-900">{user.phone}</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Loyalty Summary */}
        <Card hover className="cursor-pointer" onClick={() => navigate('/loyalty')}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-purple-100 rounded-xl">
                  <Trophy className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">Loyalty Program</h3>
                  {loyaltyMember ? (
                    <p className="text-sm text-slate-600">
                      <span className="capitalize font-medium">{loyaltyMember.tier}</span> • {loyaltyMember.points_balance?.toLocaleString() || 0} points
                    </p>
                  ) : (
                    <p className="text-sm text-slate-600">Join to earn rewards</p>
                  )}
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-slate-400" />
            </div>
          </CardContent>
        </Card>

        {/* Favorites Summary */}
        <Card hover className="cursor-pointer" onClick={() => navigate('/favorites')}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-pink-100 rounded-xl">
                  <Heart className="w-6 h-6 text-pink-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">My Favorites</h3>
                  <p className="text-sm text-slate-600">
                    {favorites?.total || 0} saved {favorites?.total === 1 ? 'place' : 'places'}
                  </p>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-slate-400" />
            </div>
          </CardContent>
        </Card>

        {/* Booking History */}
        <Card hover className="cursor-pointer" onClick={() => navigate('/bookings')}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-blue-100 rounded-xl">
                  <History className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">Booking History</h3>
                  <p className="text-sm text-slate-600">
                    {bookings?.length || 0} {bookings?.length === 1 ? 'booking' : 'bookings'}
                  </p>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-slate-400" />
            </div>
          </CardContent>
        </Card>

        {/* Payments */}
        <Card hover className="cursor-pointer" onClick={() => navigate('/payments')}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-green-100 rounded-xl">
                  <CreditCard className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">Payments</h3>
                  <p className="text-sm text-slate-600">View invoices & billing</p>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-slate-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Additional Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Preferences */}
        <Card hover className="cursor-pointer" onClick={() => navigate('/preferences')}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-indigo-100 rounded-xl">
                  <Settings className="w-6 h-6 text-indigo-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">Preferences</h3>
                  <p className="text-sm text-slate-600">Manage preferences & personalization</p>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-slate-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Guest Profile & Preferences Section */}
      {guestProfile && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Settings className="w-5 h-5 mr-2" />
              Guest Profile & Preferences
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <span className="text-sm font-semibold text-slate-700">Status:</span>
                <span className="ml-2 text-slate-900 capitalize">{guestProfile.status}</span>
              </div>
              <div>
                <span className="text-sm font-semibold text-slate-700">Marketing Consent:</span>
                <span className="ml-2 text-slate-900">{guestProfile.consentMarketing ? '✓ Yes' : '✗ No'}</span>
              </div>
              <div>
                <span className="text-sm font-semibold text-slate-700">Analytics:</span>
                <span className="ml-2 text-slate-900">{guestProfile.consentAnalytics ? '✓ Yes' : '✗ No'}</span>
              </div>
            </div>
            
            {preferences && preferences.length > 0 && (
              <div className="mt-4">
                <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center">
                  <Heart className="w-5 h-5 mr-2 text-pink-600" />
                  My Preferences
                </h3>
                <div className="space-y-3">
                  {preferences.map((pref) => (
                    <div key={pref.id} className="bg-slate-50 rounded-lg p-3 border border-slate-200">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-900 capitalize">
                          {pref.key.replace(/_/g, ' ')}
                        </span>
                        <span className="text-xs text-slate-500 capitalize">{pref.source}</span>
                      </div>
                      <div className="mt-2">
                        {Array.isArray(pref.value) ? (
                          <div className="flex flex-wrap gap-2">
                            {pref.value.map((item: string, idx: number) => (
                              <span
                                key={idx}
                                className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                              >
                                {item}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-slate-700">{String(pref.value)}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {preferences && preferences.length === 0 && (
              <p className="text-slate-500 text-sm mt-2">No preferences set yet. Your preferences will appear here as you use the platform.</p>
            )}
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="w-5 h-5 mr-2" />
              My Bookings
            </CardTitle>
          </CardHeader>
          <CardContent>
            {bookings && bookings.length > 0 ? (
              <div className="space-y-4">
                {bookings.map((booking) => (
                  <div key={booking.id} className="border-b border-slate-100 pb-4 last:border-b-0">
                    <h3 className="font-semibold text-slate-900">{booking.venueName}</h3>
                    <p className="text-sm text-slate-600">
                      {formatDate(booking.date)} at {booking.time}
                    </p>
                    <p className="text-sm text-slate-600">Party size: {booking.partySize}</p>
                    <span className={`inline-block mt-2 px-3 py-1 rounded-full text-xs font-semibold ${
                      booking.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                      booking.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                      'bg-slate-100 text-slate-800'
                    }`}>
                      {booking.status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500">No bookings yet</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Package className="w-5 h-5 mr-2" />
              My Orders
            </CardTitle>
          </CardHeader>
          <CardContent>
            {orders && orders.length > 0 ? (
              <div className="space-y-4">
                {orders.map((order) => (
                  <div key={order.id} className="border-b border-slate-100 pb-4 last:border-b-0">
                    <h3 className="font-semibold text-slate-900">{order.venueName}</h3>
                    <p className="text-sm text-slate-600">
                      {formatDateTime(order.createdAt)}
                    </p>
                    <p className="text-sm text-slate-600">
                      Total: {formatCurrency(order.total)}
                    </p>
                    <span className={`inline-block mt-2 px-3 py-1 rounded-full text-xs font-semibold ${
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
              <p className="text-slate-500">No orders yet</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

