import ApiClient from '../client';
import type {
  Booking,
  CreateBookingRequest,
  ApiResponse,
  PaginatedResponse,
  DateRange,
} from '@hospitality-platform/types';

export class BookingService {
  constructor(private client: ApiClient) {}

  async create(request: CreateBookingRequest): Promise<ApiResponse<Booking>> {
    return this.client.post('/bookings', request);
  }

  async getById(id: string): Promise<ApiResponse<Booking>> {
    return this.client.get(`/bookings/${id}`);
  }

  async getUserBookings(): Promise<ApiResponse<Booking[]>> {
    return this.client.get('/bookings/me');
  }

  async getBusinessBookings(businessId: string, dateRange?: DateRange): Promise<ApiResponse<Booking[]>> {
    return this.client.get(`/bookings/business/${businessId}`, { params: dateRange });
  }

  async update(id: string, updates: Partial<Booking>): Promise<ApiResponse<Booking>> {
    return this.client.patch(`/bookings/${id}`, updates);
  }

  async cancel(id: string): Promise<ApiResponse<Booking>> {
    return this.client.post(`/bookings/${id}/cancel`);
  }

  async checkAvailability(venueId: string, date: string, time: string): Promise<ApiResponse<{ available: boolean }>> {
    return this.client.get(`/bookings/availability`, {
      params: { venueId, date, time },
    });
  }
}

