import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Search, MapPin, Star, Heart } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Card, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import type { Venue, SearchFilters } from '@hospitality-platform/types';

export default function SearchPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [filters, setFilters] = useState<SearchFilters>({});
  const { isAuthenticated } = useAuthStore();

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

  // Get venue IDs for bulk favorite check
  const venueIds = useMemo(() => 
    searchResults?.venues?.map((v: Venue) => v.id) || [], 
    [searchResults]
  );

  // Check favorite status for all venues
  const { data: favoriteStatuses } = useQuery({
    queryKey: ['favorite-statuses', venueIds],
    queryFn: async () => {
      if (venueIds.length === 0) return { favorites: {} };
      try {
        return await apiServices.favorites.bulkCheckStatus(venueIds);
      } catch {
        return { favorites: {} };
      }
    },
    enabled: isAuthenticated && venueIds.length > 0,
  });

  const toggleFavoriteMutation = useMutation({
    mutationFn: (placeId: string) => apiServices.favorites.toggleFavorite(placeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorite-statuses'] });
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
    },
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-6 text-slate-900">Search Venues</h1>
      
      <div className="mb-8">
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for hotels, restaurants, cafes, shops..."
          leftIcon={<Search className="w-5 h-5" />}
          className="text-lg py-4"
        />
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      ) : searchResults ? (
        <div>
          <p className="text-slate-600 mb-6">
            Found <span className="font-semibold text-slate-900">{searchResults.total}</span> {searchResults.total === 1 ? 'venue' : 'venues'}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {searchResults.venues.map((venue: Venue) => (
              <Card
                key={venue.id}
                hover
                className="cursor-pointer relative group"
              >
                {isAuthenticated && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleFavoriteMutation.mutate(venue.id);
                    }}
                    disabled={toggleFavoriteMutation.isPending}
                    className="absolute top-4 right-4 z-10 p-2 bg-white/90 backdrop-blur-sm rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Heart
                      className={`w-5 h-5 transition-colors ${
                        favoriteStatuses?.favorites?.[venue.id]
                          ? 'fill-pink-500 text-pink-500'
                          : 'text-slate-600 hover:text-pink-500'
                      }`}
                    />
                  </button>
                )}
                <div onClick={() => navigate(`/venues/${venue.id}`)}>
                  {venue.images[0] && (
                    <div className="relative h-48 overflow-hidden rounded-t-2xl">
                      <img
                        src={venue.images[0]}
                        alt={venue.name}
                        className="w-full h-full object-cover hover:scale-110 transition-transform duration-300"
                      />
                    </div>
                  )}
                  <CardContent className="p-6">
                    <h3 className="text-xl font-bold text-slate-900 mb-2">{venue.name}</h3>
                    <p className="text-sm text-slate-600 mb-4 line-clamp-2">{venue.description}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-1">
                        <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                        <span className="font-semibold text-slate-900">{venue.rating}</span>
                      </div>
                      <span className="text-slate-600">{venue.priceRange}</span>
                    </div>
                  </CardContent>
                </div>
              </Card>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-12 text-slate-500">
          Enter a search query to find venues
        </div>
      )}
    </div>
  );
}

