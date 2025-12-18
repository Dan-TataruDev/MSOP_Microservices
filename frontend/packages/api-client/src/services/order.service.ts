import ApiClient from '../client';
import { MockOrderService } from './mock-order.service';
import type {
  Order,
  CreateOrderRequest,
  ApiResponse,
  PaginatedResponse,
} from '@hospitality-platform/types';

const USE_MOCK = !import.meta.env.VITE_API_BASE_URL;
const mockService = new MockOrderService();

export class OrderService {
  constructor(private client: ApiClient) {}

  async create(request: CreateOrderRequest): Promise<ApiResponse<Order>> {
    return this.client.post('/orders', request);
  }

  async getById(id: string): Promise<ApiResponse<Order>> {
    if (USE_MOCK) return mockService.getById(id);
    return this.client.get(`/orders/${id}`);
  }

  async getUserOrders(): Promise<ApiResponse<Order[]>> {
    if (USE_MOCK) return mockService.getUserOrders();
    return this.client.get('/orders/me');
  }

  async getBusinessOrders(businessId: string): Promise<ApiResponse<Order[]>> {
    if (USE_MOCK) return mockService.getBusinessOrders(businessId);
    return this.client.get(`/orders/business/${businessId}`);
  }

  async updateStatus(id: string, status: Order['status']): Promise<ApiResponse<Order>> {
    if (USE_MOCK) return mockService.updateStatus(id, status);
    return this.client.patch(`/orders/${id}/status`, { status });
  }

  async cancel(id: string): Promise<ApiResponse<Order>> {
    if (USE_MOCK) return mockService.cancel(id);
    return this.client.post(`/orders/${id}/cancel`);
  }
}

