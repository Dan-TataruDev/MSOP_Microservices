import ApiClient from '../client';
import type {
  Order,
  CreateOrderRequest,
  ApiResponse,
  PaginatedResponse,
} from '@hospitality-platform/types';

export class OrderService {
  constructor(private client: ApiClient) {}

  async create(request: CreateOrderRequest): Promise<ApiResponse<Order>> {
    return this.client.post('/orders', request);
  }

  async getById(id: string): Promise<ApiResponse<Order>> {
    return this.client.get(`/orders/${id}`);
  }

  async getUserOrders(): Promise<ApiResponse<Order[]>> {
    return this.client.get('/orders/me');
  }

  async getBusinessOrders(businessId: string): Promise<ApiResponse<Order[]>> {
    return this.client.get(`/orders/business/${businessId}`);
  }

  async updateStatus(id: string, status: Order['status']): Promise<ApiResponse<Order>> {
    return this.client.patch(`/orders/${id}/status`, { status });
  }

  async cancel(id: string): Promise<ApiResponse<Order>> {
    return this.client.post(`/orders/${id}/cancel`);
  }
}

