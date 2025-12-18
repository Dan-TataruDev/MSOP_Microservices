import ApiClient from '../client';
import { getServiceUrl } from '../config';
import type {
  InventoryItem,
  ApiResponse,
  PaginatedResponse,
} from '@hospitality-platform/types';

export class InventoryService {
  constructor(private client: ApiClient) {}

  async getInventory(businessId: string): Promise<ApiResponse<InventoryItem[]>> {
    // Backend endpoint: GET /api/v1/inventory/items?venue_id={businessId}
    const url = getServiceUrl('inventory', '/v1/inventory/items');
    return this.client.get(url, { params: { venue_id: businessId } });
  }

  async updateStock(itemId: string, quantity: number): Promise<ApiResponse<InventoryItem>> {
    // Backend endpoint: PATCH /api/v1/inventory/items/{item_id}
    const url = getServiceUrl('inventory', `/v1/inventory/items/${itemId}`);
    return this.client.patch(url, { current_stock: quantity });
  }

  async bulkUpdate(businessId: string, updates: Array<{ itemId: string; quantity: number }>): Promise<ApiResponse<InventoryItem[]>> {
    // Note: Backend may not have bulk update, using individual updates
    // This would need to be implemented as a loop or the backend needs a bulk endpoint
    const url = getServiceUrl('inventory', '/v1/inventory/items');
    return this.client.post(url, { updates });
  }

  async getLowStockItems(businessId: string): Promise<ApiResponse<InventoryItem[]>> {
    // Backend endpoint: GET /api/v1/inventory/alerts/low-stock?venue_id={businessId}
    const url = getServiceUrl('inventory', '/v1/inventory/alerts/low-stock');
    return this.client.get(url, { params: { venue_id: businessId } });
  }
}

