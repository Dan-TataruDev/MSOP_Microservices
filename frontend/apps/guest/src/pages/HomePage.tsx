import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { apiServices } from '../stores/authStore';
import { Button } from '@hospitality-platform/design-system';
import type { Venue, Recommendation } from '@hospitality-platform/types';

export default function HomePage() {
  const navigate = useNavigate();

  const { data: recommendations, isLoading } = useQuery<Recommendation[]>({
    queryKey: ['recommendations'],
    queryFn: async () => {
      const response = await apiServices.venues.getRecommendations();
      return response.data;
    },
  });

  const { data: trending } = useQuery<Venue[]>({
    queryKey: ['trending'],
    queryFn: async () => {
      const response = await apiServices.venues.getTrending(6);
      return response.data;
    },
  });

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <section className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-4">
            Discover Amazing Places
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Book hotels, order from restaurants, and shop at your favorite stores
          </p>
          <Button
            size="lg"
            onClick={() => navigate('/search')}
          >
            Start Exploring
          </Button>
        </section>

        {/* Recommendations */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : recommendations && recommendations.length > 0 ? (
          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-6">Recommended for You</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recommendations.map((rec) => (
                <div
                  key={rec.id}
                  className="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => navigate(`/venues/${rec.venueId}`)}
                >
                  {rec.venue.images[0] && (
                    <img
                      src={rec.venue.images[0]}
                      alt={rec.venue.name}
                      className="w-full h-48 object-cover"
                    />
                  )}
                  <div className="p-4">
                    <h3 className="text-lg font-semibold mb-2">{rec.venue.name}</h3>
                    <p className="text-sm text-gray-600 mb-2">{rec.reason}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-yellow-500">★ {rec.venue.rating}</span>
                      <span className="text-gray-600">{rec.venue.priceRange}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        ) : null}

        {/* Trending */}
        {trending && trending.length > 0 && (
          <section>
            <h2 className="text-2xl font-bold mb-6">Trending Now</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {trending.map((venue) => (
                <div
                  key={venue.id}
                  className="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => navigate(`/venues/${venue.id}`)}
                >
                  {venue.images[0] && (
                    <img
                      src={venue.images[0]}
                      alt={venue.name}
                      className="w-full h-48 object-cover"
                    />
                  )}
                  <div className="p-4">
                    <h3 className="text-lg font-semibold mb-2">{venue.name}</h3>
                    <p className="text-sm text-gray-600 mb-2">{venue.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-yellow-500">★ {venue.rating}</span>
                      <span className="text-gray-600">{venue.priceRange}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </Layout>
  );
}

