import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Heart, MapPin, Star, Trash2 } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';

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
          {favorites.items.map((favorite) => (
            <Card key={favorite.place_id} hover className="relative group">
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
                <div className="h-48 bg-gradient-to-br from-blue-100 to-purple-100 rounded-t-2xl flex items-center justify-center">
                  <Heart className="w-12 h-12 text-pink-400 fill-pink-400" />
                </div>
                <CardContent className="p-6">
                  <h3 className="text-lg font-bold text-slate-900 mb-2">
                    Venue #{favorite.place_id.slice(0, 8)}
                  </h3>
                  {favorite.note && (
                    <p className="text-sm text-slate-600 mb-3 line-clamp-2">{favorite.note}</p>
                  )}
                  <p className="text-xs text-slate-400">
                    Added {new Date(favorite.created_at).toLocaleDateString()}
                  </p>
                </CardContent>
              </div>
            </Card>
          ))}
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
