import ApiClient from '../client';
import { getServiceUrl } from '../config';
import { MockPaymentService } from './mock-payment.service';
import type {
  Payment,
  PaymentIntent,
  ApiResponse,
} from '@hospitality-platform/types';

export interface Invoice {
  id: string;
  invoice_number: string;
  booking_id: string;
  guest_id: string;
  amount: number;
  currency: string;
  status: string;
  issued_date: string;
  due_date?: string;
  paid_date?: string;
  items: Array<{
    description: string;
    quantity: number;
    unit_price: number;
    total: number;
  }>;
  created_at: string;
  updated_at: string;
}

export interface BillingRecord {
  id: string;
  booking_id: string;
  guest_id: string;
  amount: number;
  currency: string;
  billing_type: string;
  status: string;
  description?: string;
  created_at: string;
}

export interface Refund {
  id: string;
  refund_reference: string;
  payment_id: string;
  amount: number;
  currency: string;
  status: string;
  reason?: string;
  created_at: string;
  processed_at?: string;
}

const USE_MOCK = !import.meta.env.VITE_API_BASE_URL;
const mockService = new MockPaymentService();

export class PaymentService {
  constructor(private client: ApiClient) {}

  async createPaymentIntent(orderId: string, amount: number): Promise<ApiResponse<PaymentIntent>> {
    if (USE_MOCK) return mockService.createPaymentIntent(orderId, amount);
    const url = getServiceUrl('payments', '/v1/payments');
    return this.client.post(url, { booking_id: orderId, amount });
  }

  async confirmPayment(intentId: string): Promise<ApiResponse<Payment>> {
    if (USE_MOCK) return mockService.confirmPayment(intentId);
    const url = getServiceUrl('payments', `/v1/payments/${intentId}/confirm`);
    return this.client.post(url);
  }

  async getPayment(id: string): Promise<ApiResponse<Payment>> {
    const url = getServiceUrl('payments', `/v1/payments/${id}`);
    return this.client.get(url);
  }

  async getOrderPayment(orderId: string): Promise<ApiResponse<Payment>> {
    const url = getServiceUrl('payments', `/v1/payments/booking/${orderId}`);
    return this.client.get(url);
  }

  async getGuestPayments(guestId: string): Promise<Payment[]> {
    if (USE_MOCK) return mockService.getGuestPayments(guestId);
    const billingUrl = getServiceUrl('payments', `/v1/billing/guest/${guestId}`);
    const billingRecords = await this.client.get<BillingRecord[]>(billingUrl);
    
    const payments: Payment[] = [];
    for (const record of billingRecords) {
      try {
        const paymentUrl = getServiceUrl('payments', `/v1/payments/booking/${record.booking_id}`);
        const paymentResponse = await this.client.get<ApiResponse<Payment>>(paymentUrl);
        if (paymentResponse.data) {
          payments.push(paymentResponse.data);
        }
      } catch {
        // Skip if payment not found
      }
    }
    return payments;
  }

  async getGuestInvoices(guestId: string): Promise<Invoice[]> {
    if (USE_MOCK) return mockService.getGuestInvoices(guestId);
    const billingUrl = getServiceUrl('payments', `/v1/billing/guest/${guestId}`);
    const billingRecords = await this.client.get<BillingRecord[]>(billingUrl);
    
    const invoices: Invoice[] = [];
    for (const record of billingRecords) {
      try {
        const invoiceUrl = getServiceUrl('payments', `/v1/invoices/booking/${record.booking_id}`);
        const invoiceResponse = await this.client.get<ApiResponse<Invoice>>(invoiceUrl);
        if (invoiceResponse.data) {
          invoices.push(invoiceResponse.data);
        }
      } catch {
        // Try to get invoice by ID if available
      }
    }
    return invoices;
  }

  async getInvoice(invoiceId: string): Promise<ApiResponse<Invoice>> {
    if (USE_MOCK) return mockService.getInvoice(invoiceId);
    const url = getServiceUrl('payments', `/v1/invoices/${invoiceId}`);
    return this.client.get(url);
  }

  async getInvoiceByNumber(invoiceNumber: string): Promise<ApiResponse<Invoice>> {
    const url = getServiceUrl('payments', `/v1/invoices/number/${invoiceNumber}`);
    return this.client.get(url);
  }

  async getBookingInvoices(bookingId: string): Promise<Invoice[]> {
    if (USE_MOCK) return mockService.getBookingInvoices(bookingId);
    const url = getServiceUrl('payments', `/v1/invoices/booking/${bookingId}`);
    const response = await this.client.get<ApiResponse<Invoice[]>>(url);
    return Array.isArray(response.data) ? response.data : [response.data];
  }

  async getBillingRecords(guestId: string): Promise<BillingRecord[]> {
    if (USE_MOCK) return mockService.getBillingRecords(guestId);
    const url = getServiceUrl('payments', `/v1/billing/guest/${guestId}`);
    return this.client.get(url);
  }

  async getBookingBillingRecords(bookingId: string): Promise<BillingRecord[]> {
    if (USE_MOCK) return mockService.getBookingBillingRecords(bookingId);
    const url = getServiceUrl('payments', `/v1/billing/booking/${bookingId}`);
    return this.client.get(url);
  }

  async getRefunds(paymentId: string): Promise<Refund[]> {
    const url = getServiceUrl('payments', `/v1/refunds/payment/${paymentId}`);
    const response = await this.client.get<ApiResponse<Refund[]>>(url);
    return Array.isArray(response.data) ? response.data : [response.data];
  }

  async getRefund(refundId: string): Promise<ApiResponse<Refund>> {
    const url = getServiceUrl('payments', `/v1/refunds/${refundId}`);
    return this.client.get(url);
  }

  async refund(paymentId: string, amount?: number): Promise<ApiResponse<Payment>> {
    const url = getServiceUrl('payments', '/v1/refunds');
    return this.client.post(url, { payment_id: paymentId, amount });
  }
}

