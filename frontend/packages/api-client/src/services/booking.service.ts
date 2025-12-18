import ApiClient from '../client';
import { MockBookingService } from './mock-booking.service';
import type {
  Booking,
  CreateBookingRequest,
  ApiResponse,
  PaginatedResponse,
  DateRange,
} from '@hospitality-platform/types';

const USE_MOCK = !import.meta.env.VITE_API_BASE_URL;
const mockService = new MockBookingService();

export class BookingService {
  constructor(private client: ApiClient) {}

  async create(request: CreateBookingRequest): Promise<ApiResponse<Booking>> {
    return this.client.post('/bookings', request);
  }

  async getById(id: string): Promise<ApiResponse<Booking>> {
    if (USE_MOCK) return mockService.getById(id);
    return this.client.get(`/bookings/${id}`);
  }

  async getUserBookings(): Promise<ApiResponse<Booking[]>> {
    if (USE_MOCK) return mockService.getUserBookings();
    return this.client.get('/bookings/me');
  }

  async getBusinessBookings(businessId: string, dateRange?: DateRange): Promise<ApiResponse<Booking[]>> {
    if (USE_MOCK) return mockService.getBusinessBookings(businessId);
    return this.client.get(`/bookings/business/${businessId}`, { params: dateRange });
  }

  async update(id: string, updates: Partial<Booking>): Promise<ApiResponse<Booking>> {
    return this.client.patch(`/bookings/${id}`, updates);
  }

  async cancel(id: string): Promise<ApiResponse<Booking>> {
    if (USE_MOCK) return mockService.cancel(id);
    return this.client.post(`/bookings/${id}/cancel`);
  }

  async checkAvailability(venueId: string, date: string, time: string): Promise<ApiResponse<{ available: boolean }>> {
    if (USE_MOCK) return mockService.checkAvailability(venueId, date, time);
    return this.client.get(`/bookings/availability`, {
      params: { venueId, date, time },
    });
  }
}

