import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { apiServices } from '../stores/authStore';
import { useAuthStore } from '../stores/authStore';
import { Button } from '@hospitality-platform/design-system';
import { formatCurrency } from '@hospitality-platform/utils';

export default function VenueDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  const { data: venue, isLoading } = useQuery({
    queryKey: ['venue', id],
    queryFn: async () => {
      if (!id) throw new Error('Venue ID is required');
      const response = await apiServices.venues.getById(id);
      return response.data;
    },
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        </div>
      </Layout>
    );
  }

  if (!venue) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4">Venue not found</h1>
            <Button onClick={() => navigate('/')}>Go Home</Button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {venue.images[0] && (
            <img
              src={venue.images[0]}
              alt={venue.name}
              className="w-full h-96 object-cover"
            />
          )}
          <div className="p-6">
            <h1 className="text-3xl font-bold mb-4">{venue.name}</h1>
            <div className="flex items-center space-x-4 mb-4">
              <span className="text-yellow-500 text-xl">★ {venue.rating}</span>
              <span className="text-gray-600">{venue.reviewCount} reviews</span>
              <span className="text-gray-600">{venue.priceRange}</span>
            </div>
            <p className="text-gray-700 mb-6">{venue.description}</p>
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-2">Address</h2>
              <p className="text-gray-600">
                {venue.address.street}, {venue.address.city}, {venue.address.state} {venue.address.zipCode}
              </p>
            </div>
            <div className="flex space-x-4">
              {venue.type === 'hotel' || venue.type === 'restaurant' ? (
                <Button
                  onClick={() => {
                    if (isAuthenticated) {
                      navigate(`/bookings/${venue.id}`);
                    } else {
                      navigate('/login');
                    }
                  }}
                >
                  Make a Booking
                </Button>
              ) : null}
              {(venue.type === 'restaurant' || venue.type === 'cafe' || venue.type === 'retail') && (
                <Button
                  variant="secondary"
                  onClick={() => {
                    if (isAuthenticated) {
                      navigate(`/orders/${venue.id}`);
                    } else {
                      navigate('/login');
                    }
                  }}
                >
                  Place an Order
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

