import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Heart, MapPin, Star, Trash2, Building2 } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';

// Venue info mapping for display
const VENUE_INFO: Record<string, { name: string; type: string; rating: number; image: string }> = {
  '1': { name: 'The Grand Hotel', type: 'Hotel', rating: 4.8, image: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400' },
  '2': { name: 'Bella Italia Restaurant', type: 'Restaurant', rating: 4.6, image: 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400' },
  '3': { name: 'Coffee Corner', type: 'Cafe', rating: 4.7, image: 'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=400' },
  '4': { name: 'Fashion Boutique', type: 'Retail', rating: 4.5, image: 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400' },
  '5': { name: 'Sushi Master', type: 'Restaurant', rating: 4.9, image: 'https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=400' },
  '6': { name: 'Urban Retreat Hotel', type: 'Hotel', rating: 4.4, image: 'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=400' },
};

export default function FavoritesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuthStore();

  const { data: favorites, isLoading } = useQuery({
    queryKey: ['favorites'],
    queryFn: async () => {
      const response = await apiServices.favorites.listFavorites(1, 50);
      return response;
    },
    enabled: isAuthenticated,
  });

  const removeMutation = useMutation({
    mutationFn: (placeId: string) => apiServices.favorites.removeFavorite(placeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
    },
  });

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <Heart className="w-16 h-16 text-slate-300 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-slate-900 mb-2">Sign in to view favorites</h1>
        <p className="text-slate-600 mb-6">Save your favorite places and access them anytime</p>
        <Button onClick={() => navigate('/login')}>Sign In</Button>
      </div>
    );
  }

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
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">My Favorites</h1>
          <p className="text-slate-600">
            {favorites?.total || 0} saved {favorites?.total === 1 ? 'place' : 'places'}
          </p>
        </div>
        <Heart className="w-10 h-10 text-pink-500 fill-pink-500" />
      </div>

      {favorites?.items && favorites.items.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {favorites.items.map((favorite) => {
            const venue = VENUE_INFO[favorite.place_id] || {
              name: `Venue #${favorite.place_id.slice(0, 8)}`,
              type: 'Venue',
              rating: 4.5,
              image: '',
            };
            return (
              <Card key={favorite.place_id} hover className="relative group overflow-hidden">
                <div className="absolute top-4 right-4 z-10">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeMutation.mutate(favorite.place_id);
                    }}
                    className="p-2 bg-white/90 backdrop-blur-sm rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-50"
                    disabled={removeMutation.isPending}
                  >
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </button>
                </div>
                <div
                  className="cursor-pointer"
                  onClick={() => navigate(`/venues/${favorite.place_id}`)}
                >
                  {venue.image ? (
                    <div className="h-48 overflow-hidden">
                      <img
                        src={venue.image}
                        alt={venue.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    </div>
                  ) : (
                    <div className="h-48 bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                      <Building2 className="w-12 h-12 text-blue-400" />
                    </div>
                  )}
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-lg font-bold text-slate-900">{venue.name}</h3>
                        <p className="text-sm text-slate-500">{venue.type}</p>
                      </div>
                      <div className="flex items-center gap-1 bg-yellow-50 px-2 py-1 rounded-lg">
                        <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                        <span className="text-sm font-semibold text-yellow-700">{venue.rating}</span>
                      </div>
                    </div>
                    {favorite.note && (
                      <p className="text-sm text-slate-600 mb-3 line-clamp-2 italic">"{favorite.note}"</p>
                    )}
                    <p className="text-xs text-slate-400">
                      Added {new Date(favorite.created_at).toLocaleDateString()}
                    </p>
                  </CardContent>
                </div>
              </Card>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-16">
          <Heart className="w-16 h-16 text-slate-200 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 mb-2">No favorites yet</h2>
          <p className="text-slate-600 mb-6">
            Start exploring and save places you love!
          </p>
          <Button onClick={() => navigate('/search')}>Explore Venues</Button>
        </div>
      )}
    </div>
  );
}
