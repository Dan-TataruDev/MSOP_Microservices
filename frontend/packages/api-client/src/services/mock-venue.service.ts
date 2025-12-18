/**
 * Mock Venue Service
 * Provides mock venue data for development when the real venue service is not available.
 * This can be replaced with actual API calls later.
 */
import type { Venue, Recommendation, ApiResponse } from '@hospitality-platform/types';

// Mock venue data
const MOCK_VENUES: Venue[] = [
  {
    id: '1',
    name: 'The Grand Hotel',
    type: 'hotel',
    description: 'Luxurious 5-star hotel in the heart of the city with stunning views and world-class amenities.',
    address: {
      street: '123 Main Street',
      city: 'New York',
      state: 'NY',
      zipCode: '10001',
      country: 'USA',
      coordinates: { lat: 40.7128, lng: -74.0060 },
    },
    contact: {
      phone: '+1-212-555-0100',
      email: 'info@grandhotel.com',
      website: 'https://grandhotel.com',
    },
    images: [
      'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800',
      'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800',
    ],
    rating: 4.8,
    reviewCount: 1247,
    priceRange: '$$$$',
    amenities: ['WiFi', 'Pool', 'Spa', 'Restaurant', 'Gym', 'Parking'],
    openingHours: {
      monday: { open: '00:00', close: '23:59', isClosed: false },
      tuesday: { open: '00:00', close: '23:59', isClosed: false },
      wednesday: { open: '00:00', close: '23:59', isClosed: false },
      thursday: { open: '00:00', close: '23:59', isClosed: false },
      friday: { open: '00:00', close: '23:59', isClosed: false },
      saturday: { open: '00:00', close: '23:59', isClosed: false },
      sunday: { open: '00:00', close: '23:59', isClosed: false },
    },
    isAvailable: true,
    businessId: 'biz-1',
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z',
  },
  {
    id: '2',
    name: 'Bella Italia Restaurant',
    type: 'restaurant',
    description: 'Authentic Italian cuisine with fresh ingredients imported from Italy. Cozy atmosphere perfect for date nights.',
    address: {
      street: '456 Oak Avenue',
      city: 'New York',
      state: 'NY',
      zipCode: '10002',
      country: 'USA',
      coordinates: { lat: 40.7282, lng: -73.9942 },
    },
    contact: {
      phone: '+1-212-555-0200',
      email: 'reservations@bellaitalia.com',
      website: 'https://bellaitalia.com',
    },
    images: [
      'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800',
      'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800',
    ],
    rating: 4.6,
    reviewCount: 892,
    priceRange: '$$$',
    amenities: ['WiFi', 'Outdoor Seating', 'Reservations', 'Takeout'],
    openingHours: {
      monday: { open: '11:00', close: '22:00', isClosed: false },
      tuesday: { open: '11:00', close: '22:00', isClosed: false },
      wednesday: { open: '11:00', close: '22:00', isClosed: false },
      thursday: { open: '11:00', close: '22:00', isClosed: false },
      friday: { open: '11:00', close: '23:00', isClosed: false },
      saturday: { open: '11:00', close: '23:00', isClosed: false },
      sunday: { open: '12:00', close: '21:00', isClosed: false },
    },
    isAvailable: true,
    businessId: 'biz-2',
    createdAt: '2024-01-10T10:00:00Z',
    updatedAt: '2024-01-10T10:00:00Z',
  },
  {
    id: '3',
    name: 'Coffee Corner',
    type: 'cafe',
    description: 'Artisan coffee shop serving locally roasted beans and fresh pastries. Perfect spot for remote work.',
    address: {
      street: '789 Elm Street',
      city: 'New York',
      state: 'NY',
      zipCode: '10003',
      country: 'USA',
      coordinates: { lat: 40.7589, lng: -73.9851 },
    },
    contact: {
      phone: '+1-212-555-0300',
      email: 'hello@coffeecorner.com',
    },
    images: [
      'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800',
      'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=800',
    ],
    rating: 4.7,
    reviewCount: 634,
    priceRange: '$',
    amenities: ['WiFi', 'Outdoor Seating', 'Takeout', 'Pet Friendly'],
    openingHours: {
      monday: { open: '07:00', close: '18:00', isClosed: false },
      tuesday: { open: '07:00', close: '18:00', isClosed: false },
      wednesday: { open: '07:00', close: '18:00', isClosed: false },
      thursday: { open: '07:00', close: '18:00', isClosed: false },
      friday: { open: '07:00', close: '19:00', isClosed: false },
      saturday: { open: '08:00', close: '19:00', isClosed: false },
      sunday: { open: '08:00', close: '17:00', isClosed: false },
    },
    isAvailable: true,
    businessId: 'biz-3',
    createdAt: '2024-01-05T10:00:00Z',
    updatedAt: '2024-01-05T10:00:00Z',
  },
  {
    id: '4',
    name: 'Fashion Boutique',
    type: 'retail',
    description: 'Trendy clothing store featuring the latest fashion from local and international designers.',
    address: {
      street: '321 Fashion District',
      city: 'New York',
      state: 'NY',
      zipCode: '10004',
      country: 'USA',
      coordinates: { lat: 40.7505, lng: -73.9934 },
    },
    contact: {
      phone: '+1-212-555-0400',
      email: 'shop@fashionboutique.com',
      website: 'https://fashionboutique.com',
    },
    images: [
      'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800',
      'https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=800',
    ],
    rating: 4.5,
    reviewCount: 423,
    priceRange: '$$',
    amenities: ['WiFi', 'Fitting Rooms', 'Returns Accepted'],
    openingHours: {
      monday: { open: '10:00', close: '20:00', isClosed: false },
      tuesday: { open: '10:00', close: '20:00', isClosed: false },
      wednesday: { open: '10:00', close: '20:00', isClosed: false },
      thursday: { open: '10:00', close: '20:00', isClosed: false },
      friday: { open: '10:00', close: '21:00', isClosed: false },
      saturday: { open: '10:00', close: '21:00', isClosed: false },
      sunday: { open: '11:00', close: '19:00', isClosed: false },
    },
    isAvailable: true,
    businessId: 'biz-4',
    createdAt: '2024-01-08T10:00:00Z',
    updatedAt: '2024-01-08T10:00:00Z',
  },
  {
    id: '5',
    name: 'Sushi Master',
    type: 'restaurant',
    description: 'Premium sushi restaurant with master chefs and the freshest fish. Omakase experience available.',
    address: {
      street: '555 Sushi Lane',
      city: 'New York',
      state: 'NY',
      zipCode: '10005',
      country: 'USA',
      coordinates: { lat: 40.7614, lng: -73.9776 },
    },
    contact: {
      phone: '+1-212-555-0500',
      email: 'reservations@sushimaster.com',
    },
    images: [
      'https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=800',
      'https://images.unsplash.com/photo-1579952363873-27f3b1c94b5d?w=800',
    ],
    rating: 4.9,
    reviewCount: 1156,
    priceRange: '$$$$',
    amenities: ['Reservations', 'Sake Bar', 'Private Dining'],
    openingHours: {
      monday: { open: '17:00', close: '23:00', isClosed: false },
      tuesday: { open: '17:00', close: '23:00', isClosed: false },
      wednesday: { open: '17:00', close: '23:00', isClosed: false },
      thursday: { open: '17:00', close: '23:00', isClosed: false },
      friday: { open: '17:00', close: '00:00', isClosed: false },
      saturday: { open: '17:00', close: '00:00', isClosed: false },
      sunday: { open: '17:00', close: '22:00', isClosed: false },
    },
    isAvailable: true,
    businessId: 'biz-5',
    createdAt: '2024-01-12T10:00:00Z',
    updatedAt: '2024-01-12T10:00:00Z',
  },
  {
    id: '6',
    name: 'Urban Retreat Hotel',
    type: 'hotel',
    description: 'Boutique hotel offering modern comfort and style. Located in a vibrant neighborhood with easy access to attractions.',
    address: {
      street: '999 Urban Boulevard',
      city: 'New York',
      state: 'NY',
      zipCode: '10006',
      country: 'USA',
      coordinates: { lat: 40.7489, lng: -73.9680 },
    },
    contact: {
      phone: '+1-212-555-0600',
      email: 'bookings@urbanretreat.com',
      website: 'https://urbanretreat.com',
    },
    images: [
      'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800',
      'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800',
    ],
    rating: 4.4,
    reviewCount: 789,
    priceRange: '$$$',
    amenities: ['WiFi', 'Gym', 'Restaurant', 'Bar', 'Concierge'],
    openingHours: {
      monday: { open: '00:00', close: '23:59', isClosed: false },
      tuesday: { open: '00:00', close: '23:59', isClosed: false },
      wednesday: { open: '00:00', close: '23:59', isClosed: false },
      thursday: { open: '00:00', close: '23:59', isClosed: false },
      friday: { open: '00:00', close: '23:59', isClosed: false },
      saturday: { open: '00:00', close: '23:59', isClosed: false },
      sunday: { open: '00:00', close: '23:59', isClosed: false },
    },
    isAvailable: true,
    businessId: 'biz-6',
    createdAt: '2024-01-20T10:00:00Z',
    updatedAt: '2024-01-20T10:00:00Z',
  },
];

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export class MockVenueService {
  async getRecommendations(): Promise<ApiResponse<Recommendation[]>> {
    await delay(500); // Simulate network delay
    
    // Return first 3 venues as recommendations
    const recommendations: Recommendation[] = MOCK_VENUES.slice(0, 3).map((venue, index) => ({
      id: `rec-${venue.id}`,
      venueId: venue.id,
      venue,
      reason: index === 0 
        ? 'Based on your preference for luxury accommodations'
        : index === 1
        ? 'Matches your favorite cuisine type'
        : 'Popular choice in your area',
      confidence: 0.85 + Math.random() * 0.1,
      category: 'personalized',
    }));
    
    return {
      data: recommendations,
      message: 'Recommendations retrieved successfully',
    };
  }

  async getTrending(limit: number = 6): Promise<ApiResponse<Venue[]>> {
    await delay(500); // Simulate network delay
    
    // Return venues sorted by rating (trending)
    const trending = [...MOCK_VENUES]
      .sort((a, b) => b.rating - a.rating)
      .slice(0, limit);
    
    return {
      data: trending,
      message: 'Trending venues retrieved successfully',
    };
  }

  async getById(id: string): Promise<ApiResponse<Venue>> {
    await delay(300);
    
    const venue = MOCK_VENUES.find(v => v.id === id);
    
    if (!venue) {
      throw new Error('Venue not found');
    }
    
    return {
      data: venue,
      message: 'Venue retrieved successfully',
    };
  }

  async search(filters: any): Promise<ApiResponse<{ venues: Venue[]; total: number; filters: any }>> {
    await delay(500);
    
    let results = [...MOCK_VENUES];
    
    // Apply filters
    if (filters.query) {
      const query = filters.query.toLowerCase();
      results = results.filter(v => 
        v.name.toLowerCase().includes(query) ||
        v.description.toLowerCase().includes(query) ||
        v.address.city.toLowerCase().includes(query)
      );
    }
    
    if (filters.venueTypes && filters.venueTypes.length > 0) {
      results = results.filter(v => filters.venueTypes.includes(v.type));
    }
    
    if (filters.priceRange && filters.priceRange.length > 0) {
      results = results.filter(v => filters.priceRange.includes(v.priceRange));
    }
    
    return {
      data: {
        venues: results,
        total: results.length,
        filters,
      },
      message: 'Search completed successfully',
    };
  }
}


