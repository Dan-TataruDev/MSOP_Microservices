import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { apiServices } from '../stores/authStore';
import type { Venue, SearchFilters } from '@hospitality-platform/types';

export default function SearchPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({});

  const { data: searchResults, isLoading } = useQuery({
    queryKey: ['search', query, filters],
    queryFn: async () => {
      const response = await apiServices.venues.search({
        ...filters,
        query: query || undefined,
      });
      return response.data;
    },
    enabled: query.length > 0 || Object.keys(filters).length > 0,
  });

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Search Venues</h1>
        
        {/* Search Bar */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search for hotels, restaurants, cafes, shops..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Results */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : searchResults ? (
          <div>
            <p className="text-gray-600 mb-4">
              Found {searchResults.total} {searchResults.total === 1 ? 'venue' : 'venues'}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {searchResults.venues.map((venue) => (
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
                    <p className="text-sm text-gray-600 mb-2 line-clamp-2">{venue.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-yellow-500">★ {venue.rating}</span>
                      <span className="text-gray-600">{venue.priceRange}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            Enter a search query to find venues
          </div>
        )}
      </div>
    </Layout>
  );
}

