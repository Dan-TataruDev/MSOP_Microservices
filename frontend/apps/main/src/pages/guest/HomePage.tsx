import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Search, MapPin, Star, TrendingUp, Sparkles, Hotel, UtensilsCrossed, Coffee, ShoppingBag, CheckCircle, Users, Calendar, Shield, Zap } from 'lucide-react';
import { apiServices } from '@/stores/authStore';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import type { Venue, Recommendation } from '@hospitality-platform/types';

export default function HomePage() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const { data: recommendations, isLoading: recommendationsLoading, error: recommendationsError } = useQuery<Recommendation[]>({
    queryKey: ['recommendations'],
    queryFn: async () => {
      const response = await apiServices.venues.getRecommendations();
      return response.data;
    },
    retry: false, // Don't retry if endpoint doesn't exist
  });

  const { data: trending, isLoading: trendingLoading, error: trendingError } = useQuery<Venue[]>({
    queryKey: ['trending'],
    queryFn: async () => {
      const response = await apiServices.venues.getTrending(6);
      return response.data;
    },
    retry: false, // Don't retry if endpoint doesn't exist
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 via-white to-purple-50 py-20 mb-16">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto animate-fade-in">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl mb-8 shadow-2xl">
              <Sparkles className="w-12 h-12 text-white" />
            </div>
            <h1 className="text-6xl md:text-7xl font-bold text-slate-900 mb-6 leading-tight">
              Your All-in-One{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Hospitality Platform
              </span>
            </h1>
            <p className="text-2xl text-slate-600 mb-4 max-w-3xl mx-auto leading-relaxed">
              Discover, book, and order from hotels, restaurants, cafes, and retail stores all in one seamless experience
            </p>
            <p className="text-lg text-slate-500 mb-10 max-w-2xl mx-auto">
              Whether you're planning a trip, looking for a great meal, or shopping for the latest trends, we've got you covered with personalized recommendations and instant bookings.
            </p>
            
            {/* Search Bar */}
            <form onSubmit={handleSearch} className="max-w-3xl mx-auto mb-8">
              <div className="flex gap-3 shadow-xl rounded-2xl overflow-hidden">
                <div className="flex-1 relative">
                  <Input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search hotels, restaurants, cafes, shops..."
                    leftIcon={<Search className="w-5 h-5" />}
                    className="text-lg py-5 border-0"
                  />
                </div>
                <Button type="submit" size="lg" className="px-10 rounded-none">
                  Search
                </Button>
              </div>
            </form>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-12">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-1">500+</div>
                <div className="text-sm text-slate-600">Venues</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-1">50K+</div>
                <div className="text-sm text-slate-600">Happy Customers</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-1">100+</div>
                <div className="text-sm text-slate-600">Cities</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-1">4.8★</div>
                <div className="text-sm text-slate-600">Average Rating</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="container mx-auto px-4">
        {/* Categories Section */}
        <section className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">Explore by Category</h2>
            <p className="text-xl text-slate-600">Find exactly what you're looking for</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { icon: Hotel, name: 'Hotels', count: '150+', color: 'from-blue-500 to-blue-600', description: 'Luxury stays' },
              { icon: UtensilsCrossed, name: 'Restaurants', count: '200+', color: 'from-red-500 to-red-600', description: 'Fine dining' },
              { icon: Coffee, name: 'Cafes', count: '100+', color: 'from-amber-500 to-amber-600', description: 'Coffee & more' },
              { icon: ShoppingBag, name: 'Retail', count: '50+', color: 'from-purple-500 to-purple-600', description: 'Shop & discover' },
            ].map((category) => (
              <Card
                key={category.name}
                hover
                className="cursor-pointer text-center p-6"
                onClick={() => navigate(`/search?category=${category.name.toLowerCase()}`)}
              >
                <div className={`inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br ${category.color} rounded-2xl mb-4`}>
                  <category.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-1">{category.name}</h3>
                <p className="text-sm text-slate-500 mb-2">{category.count} venues</p>
                <p className="text-xs text-slate-400">{category.description}</p>
              </Card>
            ))}
          </div>
        </section>

        {/* How It Works Section */}
        <section className="mb-20 bg-gradient-to-br from-slate-50 to-blue-50 rounded-3xl p-12">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">How It Works</h2>
            <p className="text-xl text-slate-600">Simple, fast, and convenient</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: '1', title: 'Discover', description: 'Browse through hundreds of venues, restaurants, and shops. Use our smart search and filters to find exactly what you need.', icon: Search },
              { step: '2', title: 'Book & Order', description: 'Instantly book hotels, reserve tables, or place orders. All in one seamless checkout process.', icon: Calendar },
              { step: '3', title: 'Enjoy', description: 'Experience amazing places and services. Track your bookings and orders in real-time.', icon: CheckCircle },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 text-white rounded-full text-2xl font-bold mb-6">
                  {item.step}
                </div>
                <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-xl mb-4">
                  <item.icon className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-2xl font-bold text-slate-900 mb-3">{item.title}</h3>
                <p className="text-slate-600 leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Features Section */}
        <section className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">Why Choose Us</h2>
            <p className="text-xl text-slate-600">Everything you need in one platform</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: Sparkles, title: 'Personalized Recommendations', description: 'AI-powered suggestions based on your preferences and past experiences' },
              { icon: Zap, title: 'Instant Booking', description: 'Book hotels, reserve tables, and place orders instantly with real-time availability' },
              { icon: Shield, title: 'Secure & Reliable', description: 'Your data and payments are protected with bank-level security' },
              { icon: Users, title: 'Trusted by Thousands', description: 'Join over 50,000 satisfied customers who use our platform daily' },
              { icon: MapPin, title: 'Wide Coverage', description: 'Access venues in 100+ cities across the country' },
              { icon: Star, title: 'Top Rated', description: 'Only the best venues with 4.5+ star ratings make it to our platform' },
            ].map((feature, idx) => (
              <Card key={idx} hover className="p-6">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl mb-4">
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">{feature.title}</h3>
                <p className="text-slate-600">{feature.description}</p>
              </Card>
            ))}
          </div>
        </section>

        {/* Recommendations */}
        {recommendationsLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : recommendations && recommendations.length > 0 ? (
          <section className="mb-20">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-4xl font-bold text-slate-900 mb-2">Recommended for You</h2>
                <p className="text-xl text-slate-600">Personalized suggestions based on your preferences and behavior</p>
              </div>
              <TrendingUp className="w-10 h-10 text-blue-600" />
            </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommendations.map((rec) => (
              <Card
                key={rec.id}
                hover
                gradient
                className="cursor-pointer animate-slide-up"
                onClick={() => navigate(`/venues/${rec.venueId}`)}
              >
                {rec.venue.images[0] && (
                  <div className="relative h-48 overflow-hidden rounded-t-2xl">
                    <img
                      src={rec.venue.images[0]}
                      alt={rec.venue.name}
                      className="w-full h-full object-cover hover:scale-110 transition-transform duration-300"
                    />
                    <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-semibold text-blue-600">
                      {rec.category}
                    </div>
                  </div>
                )}
                <CardContent className="p-6">
                  <h3 className="text-xl font-bold text-slate-900 mb-2">{rec.venue.name}</h3>
                  <p className="text-sm text-slate-600 mb-4 line-clamp-2">{rec.reason}</p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1">
                      <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                      <span className="font-semibold text-slate-900">{rec.venue.rating}</span>
                      <span className="text-slate-500 text-sm">({rec.venue.reviewCount})</span>
                    </div>
                    <span className="text-slate-600 font-medium">{rec.venue.priceRange}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      ) : null}

        {/* Trending */}
        {trendingLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : trending && trending.length > 0 ? (
          <section className="mb-20">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-4xl font-bold text-slate-900 mb-2">Trending Now</h2>
                <p className="text-xl text-slate-600">Popular venues everyone's talking about right now</p>
              </div>
              <TrendingUp className="w-10 h-10 text-purple-600" />
            </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {trending.map((venue) => (
              <Card
                key={venue.id}
                hover
                className="cursor-pointer animate-slide-up"
                onClick={() => navigate(`/venues/${venue.id}`)}
              >
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
                    <div className="flex items-center space-x-1 text-slate-500 text-sm">
                      <MapPin className="w-4 h-4" />
                      <span>{venue.address.city}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
        ) : null}

        {/* CTA Section */}
        <section className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl p-12 text-center text-white mb-20">
          <h2 className="text-4xl font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-xl mb-8 text-blue-100 max-w-2xl mx-auto">
            Join thousands of happy customers discovering amazing places every day
          </p>
          <div className="flex gap-4 justify-center">
            <Button 
              variant="secondary" 
              size="lg" 
              className="bg-white text-blue-600 hover:bg-blue-50"
              onClick={() => navigate('/search')}
            >
              Explore Venues
            </Button>
            <Button 
              variant="outline" 
              size="lg" 
              className="border-2 border-white text-white hover:bg-white/10"
              onClick={() => navigate('/auth/register')}
            >
              Sign Up Free
            </Button>
          </div>
        </section>
      </div>
    </div>
  );
}

