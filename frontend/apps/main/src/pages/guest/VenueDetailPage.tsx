import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { MapPin, Star, Calendar, ShoppingCart, Phone, Globe, Heart, MessageSquare, X, Send } from 'lucide-react';
import { apiServices } from '@/stores/authStore';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { formatCurrency } from '@hospitality-platform/utils';

export default function VenueDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuthStore();

  const queryClient = useQueryClient();

  const { data: venue, isLoading } = useQuery({
    queryKey: ['venue', id],
    queryFn: async () => {
      if (!id) throw new Error('Venue ID is required');
      const response = await apiServices.venues.getById(id);
      return response.data;
    },
    enabled: !!id,
  });

  // Check favorite status
  const { data: favoriteStatus } = useQuery({
    queryKey: ['favorite-status', id],
    queryFn: async () => {
      if (!id) return { is_favorited: false };
      try {
        return await apiServices.favorites.checkStatus(id);
      } catch {
        return { is_favorited: false };
      }
    },
    enabled: !!id && isAuthenticated,
  });

  const toggleFavoriteMutation = useMutation({
    mutationFn: (placeId: string) => apiServices.favorites.toggleFavorite(placeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorite-status', id] });
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
    },
  });

  // Feedback state
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState(5);
  const [feedbackCategory, setFeedbackCategory] = useState<'service' | 'food' | 'ambiance' | 'cleanliness' | 'value' | 'overall'>('overall');
  const [feedbackComment, setFeedbackComment] = useState('');
  const [submittedFeedback, setSubmittedFeedback] = useState<string | null>(null);

  const feedbackMutation = useMutation({
    mutationFn: async () => {
      if (!id) throw new Error('Venue ID required');
      return await apiServices.feedback.submitFeedback({
        venue_id: id,
        category: feedbackCategory,
        rating: feedbackRating,
        comment: feedbackComment || undefined,
      });
    },
    onSuccess: (data) => {
      setSubmittedFeedback(data.feedback_reference);
      setShowFeedbackForm(false);
      setFeedbackComment('');
      setFeedbackRating(5);
    },
  });

  // Track venue view interaction
  useEffect(() => {
    const trackVenueView = async () => {
      if (!id || !isAuthenticated || !user?.id) return;

      try {
        // Get interaction types
        const { data: types } = await apiServices.personalization.getInteractionTypes();
        const viewType = types.find((t: any) => t.name === 'venue_viewed');
        
        if (viewType) {
          // Record the interaction
          await apiServices.personalization.createInteraction(user.id, {
            interactionTypeId: viewType.id,
            entityType: 'venue',
            entityId: id,
            source: 'frontend',
          });
        }
      } catch (error) {
        // Silently fail - interaction tracking shouldn't break the page
        console.debug('Failed to track venue view:', error);
      }
    };

    if (venue && isAuthenticated) {
      trackVenueView();
    }
  }, [id, venue, isAuthenticated, user?.id]);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  if (!venue) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Venue not found</h1>
          <Button onClick={() => navigate('/')}>Go Home</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Card className="overflow-hidden">
        {venue.images[0] && (
          <div className="relative h-96 overflow-hidden">
            <img
              src={venue.images[0]}
              alt={venue.name}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
            <div className="absolute top-4 right-4">
              {isAuthenticated && (
                <button
                  onClick={() => id && toggleFavoriteMutation.mutate(id)}
                  disabled={toggleFavoriteMutation.isPending}
                  className="p-3 bg-white/90 backdrop-blur-sm rounded-full shadow-lg hover:bg-white transition-colors"
                >
                  <Heart
                    className={`w-6 h-6 transition-colors ${
                      favoriteStatus?.is_favorited
                        ? 'fill-pink-500 text-pink-500'
                        : 'text-slate-600 hover:text-pink-500'
                    }`}
                  />
                </button>
              )}
            </div>
            <div className="absolute bottom-6 left-6 right-6">
              <h1 className="text-4xl font-bold text-white mb-2">{venue.name}</h1>
              <div className="flex items-center space-x-4 text-white/90">
                <div className="flex items-center space-x-1">
                  <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                  <span className="font-semibold">{venue.rating}</span>
                  <span className="text-sm">({venue.reviewCount} reviews)</span>
                </div>
                <span>{venue.priceRange}</span>
              </div>
            </div>
          </div>
        )}
        <CardContent className="p-8">
          <p className="text-lg text-slate-700 mb-6">{venue.description}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div>
              <h3 className="font-semibold text-slate-900 mb-2 flex items-center">
                <MapPin className="w-5 h-5 mr-2 text-blue-600" />
                Address
              </h3>
              <p className="text-slate-600">
                {venue.address.street}, {venue.address.city}, {venue.address.state} {venue.address.zipCode}
              </p>
            </div>
            {venue.contact.phone && (
              <div>
                <h3 className="font-semibold text-slate-900 mb-2 flex items-center">
                  <Phone className="w-5 h-5 mr-2 text-blue-600" />
                  Contact
                </h3>
                <p className="text-slate-600">{venue.contact.phone}</p>
              </div>
            )}
            {venue.contact.website && (
              <div>
                <h3 className="font-semibold text-slate-900 mb-2 flex items-center">
                  <Globe className="w-5 h-5 mr-2 text-blue-600" />
                  Website
                </h3>
                <a href={venue.contact.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                  {venue.contact.website}
                </a>
              </div>
            )}
          </div>

          <div className="flex flex-wrap gap-4">
            {venue.type === 'hotel' || venue.type === 'restaurant' ? (
              <Button
                onClick={() => {
                  if (isAuthenticated) {
                    navigate(`/bookings/${venue.id}`);
                  } else {
                    navigate('/login');
                  }
                }}
                leftIcon={<Calendar className="w-5 h-5" />}
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
                leftIcon={<ShoppingCart className="w-5 h-5" />}
              >
                Place an Order
              </Button>
            )}
            {isAuthenticated && (
              <Button
                variant="outline"
                onClick={() => setShowFeedbackForm(true)}
                leftIcon={<MessageSquare className="w-5 h-5" />}
              >
                Leave Feedback
              </Button>
            )}
          </div>

          {/* Feedback Success Message */}
          {submittedFeedback && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-xl">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-800 font-medium">Thank you for your feedback!</p>
                  <p className="text-sm text-green-600">Reference: {submittedFeedback}</p>
                </div>
                <button onClick={() => setSubmittedFeedback(null)} className="text-green-600 hover:text-green-800">
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Feedback Modal */}
      {showFeedbackForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-slate-900">Leave Feedback</h3>
                <button onClick={() => setShowFeedbackForm(false)} className="text-slate-400 hover:text-slate-600">
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                {/* Rating */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Rating</label>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map((rating) => (
                      <button
                        key={rating}
                        onClick={() => setFeedbackRating(rating)}
                        className="p-1"
                      >
                        <Star
                          className={`w-8 h-8 transition-colors ${
                            rating <= feedbackRating
                              ? 'fill-yellow-400 text-yellow-400'
                              : 'text-slate-300'
                          }`}
                        />
                      </button>
                    ))}
                  </div>
                </div>

                {/* Category */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Category</label>
                  <select
                    value={feedbackCategory}
                    onChange={(e) => setFeedbackCategory(e.target.value as any)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="overall">Overall Experience</option>
                    <option value="service">Service</option>
                    <option value="food">Food & Drinks</option>
                    <option value="ambiance">Ambiance</option>
                    <option value="cleanliness">Cleanliness</option>
                    <option value="value">Value for Money</option>
                  </select>
                </div>

                {/* Comment */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Comment (optional)</label>
                  <textarea
                    value={feedbackComment}
                    onChange={(e) => setFeedbackComment(e.target.value)}
                    placeholder="Tell us about your experience..."
                    rows={3}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  />
                </div>

                <Button
                  onClick={() => feedbackMutation.mutate()}
                  disabled={feedbackMutation.isPending}
                  className="w-full"
                  leftIcon={<Send className="w-5 h-5" />}
                >
                  {feedbackMutation.isPending ? 'Submitting...' : 'Submit Feedback'}
                </Button>

                {feedbackMutation.isError && (
                  <p className="text-sm text-red-600 text-center">
                    Failed to submit feedback. Please try again.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

