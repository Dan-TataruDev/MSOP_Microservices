import ApiClient from '../client';
import { getServiceUrl } from '../config';
import { MockInventoryService } from './mock-business.service';
import type { InventoryItem, ApiResponse, PaginatedResponse } from '@hospitality-platform/types';

const USE_MOCK = !import.meta.env.VITE_API_BASE_URL;
const mockService = new MockInventoryService();

export class InventoryService {
  constructor(private client: ApiClient) {}

  async getInventory(businessId: string): Promise<ApiResponse<InventoryItem[]>> {
    if (USE_MOCK) return mockService.getInventory(businessId);
    const url = getServiceUrl('inventory', '/v1/inventory/items');
    return this.client.get(url, { params: { venue_id: businessId } });
  }

  async updateStock(itemId: string, quantity: number): Promise<ApiResponse<InventoryItem>> {
    if (USE_MOCK) return mockService.updateStock(itemId, quantity);
    const url = getServiceUrl('inventory', `/v1/inventory/items/${itemId}`);
    return this.client.patch(url, { current_stock: quantity });
  }

  async bulkUpdate(businessId: string, updates: Array<{ itemId: string; quantity: number }>): Promise<ApiResponse<InventoryItem[]>> {
    const url = getServiceUrl('inventory', '/v1/inventory/items');
    return this.client.post(url, { updates });
  }

  async getLowStockItems(businessId: string): Promise<ApiResponse<InventoryItem[]>> {
    if (USE_MOCK) return mockService.getLowStockItems(businessId);
    const url = getServiceUrl('inventory', '/v1/inventory/alerts/low-stock');
    return this.client.get(url, { params: { venue_id: businessId } });
  }
}

