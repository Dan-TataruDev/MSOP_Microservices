/**
 * Mock Payment Service
 * Provides mock payment, invoice, and billing data for development.
 */
import type { Invoice, BillingRecord, Refund } from './payment.service';
import type { Payment, PaymentIntent, ApiResponse } from '@hospitality-platform/types';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Generate a unique ID
const generateId = () => Math.random().toString(36).substr(2, 9);

// Mock payments data
const MOCK_PAYMENTS: Record<string, Payment[]> = {};
const MOCK_INVOICES: Record<string, Invoice[]> = {};
const MOCK_BILLING: Record<string, BillingRecord[]> = {};

function initializeUserData(guestId: string) {
  if (MOCK_PAYMENTS[guestId]) return;

  const now = Date.now();
  const bookingIds = [`bk-${generateId()}`, `bk-${generateId()}`, `bk-${generateId()}`, `bk-${generateId()}`];

  // Create mock payments
  MOCK_PAYMENTS[guestId] = [
    {
      id: `pay-${generateId()}`,
      orderId: bookingIds[0],
      userId: guestId,
      amount: 450.00,
      currency: 'USD',
      status: 'completed',
      paymentMethod: 'credit_card',
      createdAt: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `pay-${generateId()}`,
      orderId: bookingIds[1],
      userId: guestId,
      amount: 125.50,
      currency: 'USD',
      status: 'completed',
      paymentMethod: 'credit_card',
      createdAt: new Date(now - 15 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 15 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `pay-${generateId()}`,
      orderId: bookingIds[2],
      userId: guestId,
      amount: 89.99,
      currency: 'USD',
      status: 'refunded',
      paymentMethod: 'debit_card',
      createdAt: new Date(now - 30 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 25 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `pay-${generateId()}`,
      orderId: bookingIds[3],
      userId: guestId,
      amount: 275.00,
      currency: 'USD',
      status: 'pending',
      paymentMethod: 'credit_card',
      createdAt: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ] as Payment[];

  // Create mock invoices
  MOCK_INVOICES[guestId] = [
    {
      id: `inv-${generateId()}`,
      invoice_number: 'INV-2024-001',
      booking_id: bookingIds[0],
      guest_id: guestId,
      amount: 450.00,
      currency: 'USD',
      status: 'paid',
      issued_date: new Date(now - 6 * 24 * 60 * 60 * 1000).toISOString(),
      due_date: new Date(now + 24 * 24 * 60 * 60 * 1000).toISOString(),
      paid_date: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(),
      items: [
        { description: 'Deluxe Room - 2 Nights', quantity: 2, unit_price: 200, total: 400 },
        { description: 'Room Service', quantity: 1, unit_price: 35, total: 35 },
        { description: 'Parking', quantity: 2, unit_price: 7.50, total: 15 },
      ],
      created_at: new Date(now - 6 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `inv-${generateId()}`,
      invoice_number: 'INV-2024-002',
      booking_id: bookingIds[1],
      guest_id: guestId,
      amount: 125.50,
      currency: 'USD',
      status: 'paid',
      issued_date: new Date(now - 16 * 24 * 60 * 60 * 1000).toISOString(),
      due_date: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(),
      paid_date: new Date(now - 15 * 24 * 60 * 60 * 1000).toISOString(),
      items: [
        { description: 'Dinner for 2 - Italian Set Menu', quantity: 2, unit_price: 55, total: 110 },
        { description: 'Wine Selection', quantity: 1, unit_price: 15.50, total: 15.50 },
      ],
      created_at: new Date(now - 16 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(now - 15 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `inv-${generateId()}`,
      invoice_number: 'INV-2024-003',
      booking_id: bookingIds[3],
      guest_id: guestId,
      amount: 275.00,
      currency: 'USD',
      status: 'pending',
      issued_date: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(),
      due_date: new Date(now + 14 * 24 * 60 * 60 * 1000).toISOString(),
      items: [
        { description: 'Standard Room - 1 Night', quantity: 1, unit_price: 225, total: 225 },
        { description: 'Breakfast Buffet', quantity: 2, unit_price: 25, total: 50 },
      ],
      created_at: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ];

  // Create mock billing records
  MOCK_BILLING[guestId] = [
    {
      id: `bill-${generateId()}`,
      booking_id: bookingIds[0],
      guest_id: guestId,
      amount: 450.00,
      currency: 'USD',
      billing_type: 'accommodation',
      status: 'paid',
      description: 'Hotel stay - The Grand Hotel',
      created_at: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `bill-${generateId()}`,
      booking_id: bookingIds[1],
      guest_id: guestId,
      amount: 125.50,
      currency: 'USD',
      billing_type: 'dining',
      status: 'paid',
      description: 'Dinner - Bella Italia Restaurant',
      created_at: new Date(now - 15 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `bill-${generateId()}`,
      booking_id: bookingIds[2],
      guest_id: guestId,
      amount: 89.99,
      currency: 'USD',
      billing_type: 'dining',
      status: 'refunded',
      description: 'Cancelled reservation - Sushi Master',
      created_at: new Date(now - 30 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `bill-${generateId()}`,
      booking_id: bookingIds[3],
      guest_id: guestId,
      amount: 275.00,
      currency: 'USD',
      billing_type: 'accommodation',
      status: 'pending',
      description: 'Upcoming stay - Urban Retreat Hotel',
      created_at: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `bill-${generateId()}`,
      booking_id: bookingIds[0],
      guest_id: guestId,
      amount: 75.00,
      currency: 'USD',
      billing_type: 'spa',
      status: 'paid',
      description: 'Spa Treatment - Massage',
      created_at: new Date(now - 4 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ];
}

export class MockPaymentService {
  async createPaymentIntent(orderId: string, amount: number): Promise<ApiResponse<PaymentIntent>> {
    await delay(400);
    return {
      data: {
        id: `pi-${generateId()}`,
        clientSecret: `secret-${generateId()}`,
        amount,
        currency: 'USD',
        status: 'requires_payment_method',
      } as PaymentIntent,
      message: 'Payment intent created',
    };
  }

  async confirmPayment(intentId: string): Promise<ApiResponse<Payment>> {
    await delay(500);
    return {
      data: {
        id: intentId,
        status: 'completed',
        amount: 100,
        currency: 'USD',
      } as Payment,
      message: 'Payment confirmed',
    };
  }

  async getGuestPayments(guestId: string): Promise<Payment[]> {
    await delay(300);
    initializeUserData(guestId);
    return MOCK_PAYMENTS[guestId] || [];
  }

  async getGuestInvoices(guestId: string): Promise<Invoice[]> {
    await delay(300);
    initializeUserData(guestId);
    return MOCK_INVOICES[guestId] || [];
  }

  async getBillingRecords(guestId: string): Promise<BillingRecord[]> {
    await delay(300);
    initializeUserData(guestId);
    return MOCK_BILLING[guestId] || [];
  }

  async getInvoice(invoiceId: string): Promise<ApiResponse<Invoice>> {
    await delay(200);
    for (const invoices of Object.values(MOCK_INVOICES)) {
      const invoice = invoices.find(i => i.id === invoiceId);
      if (invoice) {
        return { data: invoice, message: 'Invoice found' };
      }
    }
    throw new Error('Invoice not found');
  }

  async getBookingInvoices(bookingId: string): Promise<Invoice[]> {
    await delay(200);
    for (const invoices of Object.values(MOCK_INVOICES)) {
      const matching = invoices.filter(i => i.booking_id === bookingId);
      if (matching.length > 0) return matching;
    }
    return [];
  }

  async getBookingBillingRecords(bookingId: string): Promise<BillingRecord[]> {
    await delay(200);
    for (const records of Object.values(MOCK_BILLING)) {
      const matching = records.filter(r => r.booking_id === bookingId);
      if (matching.length > 0) return matching;
    }
    return [];
  }
}
