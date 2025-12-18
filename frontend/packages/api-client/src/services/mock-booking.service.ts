/**
 * Mock Booking Service
 * Provides mock booking data for development.
 */
import type { Booking, ApiResponse } from '@hospitality-platform/types';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const generateId = () => Math.random().toString(36).substr(2, 9);

// Store user bookings in memory
const MOCK_USER_BOOKINGS: Record<string, Booking[]> = {};

const VENUE_DATA = [
  { id: '1', name: 'The Grand Hotel', address: '123 Main Street, New York, NY' },
  { id: '2', name: 'Bella Italia Restaurant', address: '456 Oak Avenue, New York, NY' },
  { id: '3', name: 'Coffee Corner', address: '789 Elm Street, New York, NY' },
  { id: '5', name: 'Sushi Master', address: '555 Sushi Lane, New York, NY' },
  { id: '6', name: 'Urban Retreat Hotel', address: '999 Urban Boulevard, New York, NY' },
];

function initializeUserBookings(userId: string) {
  if (MOCK_USER_BOOKINGS[userId]) return;

  const now = Date.now();
  const statuses: Array<Booking['status']> = ['confirmed', 'pending', 'completed', 'cancelled', 'checked_in'];

  MOCK_USER_BOOKINGS[userId] = [
    {
      id: `bk-${generateId()}`,
      venueId: '1',
      venueName: 'The Grand Hotel',
      userId,
      date: new Date(now + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      time: '15:00',
      partySize: 2,
      status: 'confirmed',
      totalAmount: 450,
      currency: 'USD',
      specialRequests: 'Late check-in requested',
      bookingReference: `GH-${generateId().toUpperCase()}`,
      venueAddress: '123 Main Street, New York, NY',
      createdAt: new Date(now - 3 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 3 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `bk-${generateId()}`,
      venueId: '2',
      venueName: 'Bella Italia Restaurant',
      userId,
      date: new Date(now + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      time: '19:30',
      partySize: 4,
      status: 'confirmed',
      totalAmount: 200,
      currency: 'USD',
      specialRequests: 'Window seat preferred, anniversary dinner',
      bookingReference: `BI-${generateId().toUpperCase()}`,
      venueAddress: '456 Oak Avenue, New York, NY',
      createdAt: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `bk-${generateId()}`,
      venueId: '5',
      venueName: 'Sushi Master',
      userId,
      date: new Date(now - 10 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      time: '20:00',
      partySize: 2,
      status: 'completed',
      totalAmount: 180,
      currency: 'USD',
      bookingReference: `SM-${generateId().toUpperCase()}`,
      venueAddress: '555 Sushi Lane, New York, NY',
      createdAt: new Date(now - 15 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 10 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `bk-${generateId()}`,
      venueId: '6',
      venueName: 'Urban Retreat Hotel',
      userId,
      date: new Date(now - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      time: '14:00',
      partySize: 2,
      status: 'completed',
      totalAmount: 320,
      currency: 'USD',
      specialRequests: 'High floor room',
      bookingReference: `UR-${generateId().toUpperCase()}`,
      venueAddress: '999 Urban Boulevard, New York, NY',
      createdAt: new Date(now - 35 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 30 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `bk-${generateId()}`,
      venueId: '3',
      venueName: 'Coffee Corner',
      userId,
      date: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      time: '10:00',
      partySize: 3,
      status: 'cancelled',
      totalAmount: 45,
      currency: 'USD',
      bookingReference: `CC-${generateId().toUpperCase()}`,
      venueAddress: '789 Elm Street, New York, NY',
      createdAt: new Date(now - 8 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 6 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `bk-${generateId()}`,
      venueId: '1',
      venueName: 'The Grand Hotel',
      userId,
      date: new Date(now + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      time: '12:00',
      partySize: 1,
      status: 'pending',
      totalAmount: 275,
      currency: 'USD',
      specialRequests: 'Business trip, need desk in room',
      bookingReference: `GH-${generateId().toUpperCase()}`,
      venueAddress: '123 Main Street, New York, NY',
      createdAt: new Date(now - 2 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 2 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ] as Booking[];
}

export class MockBookingService {
  async getUserBookings(): Promise<ApiResponse<Booking[]>> {
    await delay(400);
    // Use a default user ID - in real usage, this would come from auth
    const userId = 'mock-user';
    initializeUserBookings(userId);
    return {
      data: MOCK_USER_BOOKINGS[userId] || [],
      message: 'Bookings retrieved successfully',
    };
  }

  async getById(id: string): Promise<ApiResponse<Booking>> {
    await delay(200);
    for (const bookings of Object.values(MOCK_USER_BOOKINGS)) {
      const booking = bookings.find(b => b.id === id);
      if (booking) {
        return { data: booking, message: 'Booking found' };
      }
    }
    throw new Error('Booking not found');
  }

  async cancel(id: string): Promise<ApiResponse<Booking>> {
    await delay(300);
    for (const bookings of Object.values(MOCK_USER_BOOKINGS)) {
      const booking = bookings.find(b => b.id === id);
      if (booking) {
        booking.status = 'cancelled';
        booking.updatedAt = new Date().toISOString();
        return { data: booking, message: 'Booking cancelled' };
      }
    }
    throw new Error('Booking not found');
  }

  async checkAvailability(venueId: string, date: string, time: string): Promise<ApiResponse<{ available: boolean }>> {
    await delay(200);
    const dateObj = new Date(date);
    const isWeekend = dateObj.getDay() === 0 || dateObj.getDay() === 6;
    const isEvening = parseInt(time.split(':')[0]) >= 18;
    const available = !(isWeekend && isEvening && Math.random() > 0.5);
    return { data: { available }, message: 'Availability checked' };
  }

  async getBusinessBookings(businessId: string): Promise<ApiResponse<Booking[]>> {
    await delay(400);
    const now = Date.now();
    const mockBusinessBookings: Booking[] = [
      {
        id: `bk-biz-${generateId()}`,
        venueId: '1',
        venueName: 'The Grand Hotel',
        userId: 'guest-1',
        date: new Date(now + 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        time: '14:00',
        partySize: 2,
        status: 'confirmed',
        totalAmount: 450,
        currency: 'USD',
        specialRequests: 'Early check-in if possible',
        bookingReference: `BIZ-${generateId().toUpperCase()}`,
        createdAt: new Date(now - 2 * 24 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date(now - 2 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: `bk-biz-${generateId()}`,
        venueId: '1',
        venueName: 'The Grand Hotel',
        userId: 'guest-2',
        date: new Date(now + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        time: '15:00',
        partySize: 4,
        status: 'confirmed',
        totalAmount: 780,
        currency: 'USD',
        bookingReference: `BIZ-${generateId().toUpperCase()}`,
        createdAt: new Date(now - 3 * 24 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date(now - 3 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: `bk-biz-${generateId()}`,
        venueId: '1',
        venueName: 'The Grand Hotel',
        userId: 'guest-3',
        date: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        time: '12:00',
        partySize: 1,
        status: 'completed',
        totalAmount: 225,
        currency: 'USD',
        bookingReference: `BIZ-${generateId().toUpperCase()}`,
        createdAt: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: `bk-biz-${generateId()}`,
        venueId: '1',
        venueName: 'The Grand Hotel',
        userId: 'guest-4',
        date: new Date(now + 5 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        time: '16:00',
        partySize: 3,
        status: 'pending',
        totalAmount: 650,
        currency: 'USD',
        specialRequests: 'Connecting rooms please',
        bookingReference: `BIZ-${generateId().toUpperCase()}`,
        createdAt: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: `bk-biz-${generateId()}`,
        venueId: '1',
        venueName: 'The Grand Hotel',
        userId: 'guest-5',
        date: new Date(now - 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        time: '11:00',
        partySize: 2,
        status: 'cancelled',
        totalAmount: 350,
        currency: 'USD',
        bookingReference: `BIZ-${generateId().toUpperCase()}`,
        createdAt: new Date(now - 7 * 24 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date(now - 4 * 24 * 60 * 60 * 1000).toISOString(),
      },
    ] as Booking[];
    
    return {
      data: mockBusinessBookings,
      message: 'Business bookings retrieved',
    };
  }
}
