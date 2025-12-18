import ApiClient from '../client';
import { getServiceUrl } from '../config';
import type {
  Venue,
  SearchFilters,
  SearchResult,
  Recommendation,
  ApiResponse,
  PaginatedResponse,
} from '@hospitality-platform/types';
import { MockVenueService } from './mock-venue.service';

// Use mock service when real API is not available
const USE_MOCK_SERVICE = import.meta.env.VITE_USE_MOCK_VENUES === 'true' || 
                         !import.meta.env.VITE_VENUE_SERVICE_URL;

const mockService = new MockVenueService();

export class VenueService {
  constructor(private client: ApiClient) {}

  async search(filters: SearchFilters): Promise<ApiResponse<SearchResult>> {
    if (USE_MOCK_SERVICE) {
      return mockService.search(filters);
    }
    return this.client.post('/venues/search', filters);
  }

  async getById(id: string): Promise<ApiResponse<Venue>> {
    if (USE_MOCK_SERVICE) {
      return mockService.getById(id);
    }
    return this.client.get(`/venues/${id}`);
  }

  async getRecommendations(): Promise<ApiResponse<Recommendation[]>> {
    if (USE_MOCK_SERVICE) {
      return mockService.getRecommendations();
    }
    // Use guest-interaction-service URL for recommendations endpoint
    return this.client.get(getServiceUrl('venues', '/venues/recommendations'));
  }

  async getTrending(limit?: number): Promise<ApiResponse<Venue[]>> {
    if (USE_MOCK_SERVICE) {
      return mockService.getTrending(limit);
    }
    // Use guest-interaction-service URL for trending endpoint
    return this.client.get(getServiceUrl('venues', '/venues/trending'), { params: { limit } });
  }

  async getNearby(lat: number, lng: number, radius?: number): Promise<ApiResponse<Venue[]>> {
    if (USE_MOCK_SERVICE) {
      // For mock, return all venues (in real app, would filter by location)
      return mockService.getTrending(10);
    }
    return this.client.get('/venues/nearby', { params: { lat, lng, radius } });
  }
}

