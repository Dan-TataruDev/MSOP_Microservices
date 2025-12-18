/**
 * Mock Order Service
 * Provides mock order data for development.
 */
import type { Order, ApiResponse } from '@hospitality-platform/types';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const generateId = () => Math.random().toString(36).substr(2, 9);

// Store user orders in memory
const MOCK_USER_ORDERS: Record<string, Order[]> = {};

function initializeUserOrders(userId: string) {
  if (MOCK_USER_ORDERS[userId]) return;

  const now = Date.now();

  MOCK_USER_ORDERS[userId] = [
    {
      id: `ord-${generateId()}`,
      venueId: '2',
      venueName: 'Bella Italia Restaurant',
      userId,
      items: [
        { id: '1', name: 'Margherita Pizza', quantity: 1, price: 18.99, total: 18.99 },
        { id: '2', name: 'Pasta Carbonara', quantity: 1, price: 22.50, total: 22.50 },
        { id: '3', name: 'Tiramisu', quantity: 2, price: 9.99, total: 19.98 },
        { id: '4', name: 'House Red Wine', quantity: 1, price: 12.00, total: 12.00 },
      ],
      subtotal: 73.47,
      tax: 6.61,
      total: 80.08,
      status: 'delivered',
      orderType: 'dine_in',
      createdAt: new Date(now - 2 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 2 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `ord-${generateId()}`,
      venueId: '3',
      venueName: 'Coffee Corner',
      userId,
      items: [
        { id: '1', name: 'Cappuccino', quantity: 2, price: 4.50, total: 9.00 },
        { id: '2', name: 'Croissant', quantity: 2, price: 3.50, total: 7.00 },
        { id: '3', name: 'Avocado Toast', quantity: 1, price: 12.00, total: 12.00 },
      ],
      subtotal: 28.00,
      tax: 2.52,
      total: 30.52,
      status: 'delivered',
      orderType: 'takeout',
      createdAt: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `ord-${generateId()}`,
      venueId: '5',
      venueName: 'Sushi Master',
      userId,
      items: [
        { id: '1', name: 'Omakase Set', quantity: 2, price: 85.00, total: 170.00 },
        { id: '2', name: 'Sake Carafe', quantity: 1, price: 25.00, total: 25.00 },
        { id: '3', name: 'Miso Soup', quantity: 2, price: 5.00, total: 10.00 },
      ],
      subtotal: 205.00,
      tax: 18.45,
      total: 223.45,
      status: 'delivered',
      orderType: 'dine_in',
      createdAt: new Date(now - 10 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 10 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `ord-${generateId()}`,
      venueId: '1',
      venueName: 'The Grand Hotel - Room Service',
      userId,
      items: [
        { id: '1', name: 'Club Sandwich', quantity: 1, price: 24.00, total: 24.00 },
        { id: '2', name: 'Fresh Orange Juice', quantity: 1, price: 8.00, total: 8.00 },
        { id: '3', name: 'Chocolate Cake', quantity: 1, price: 12.00, total: 12.00 },
      ],
      subtotal: 44.00,
      tax: 3.96,
      total: 47.96,
      status: 'delivered',
      orderType: 'room_service',
      createdAt: new Date(now - 7 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 7 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `ord-${generateId()}`,
      venueId: '2',
      venueName: 'Bella Italia Restaurant',
      userId,
      items: [
        { id: '1', name: 'Lasagna', quantity: 1, price: 19.99, total: 19.99 },
        { id: '2', name: 'Caesar Salad', quantity: 1, price: 14.50, total: 14.50 },
      ],
      subtotal: 34.49,
      tax: 3.10,
      total: 37.59,
      status: 'preparing',
      orderType: 'delivery',
      createdAt: new Date(now - 30 * 60 * 1000).toISOString(), // 30 minutes ago
      updatedAt: new Date(now - 15 * 60 * 1000).toISOString(),
    },
    {
      id: `ord-${generateId()}`,
      venueId: '3',
      venueName: 'Coffee Corner',
      userId,
      items: [
        { id: '1', name: 'Latte', quantity: 1, price: 5.00, total: 5.00 },
      ],
      subtotal: 5.00,
      tax: 0.45,
      total: 5.45,
      status: 'cancelled',
      orderType: 'takeout',
      createdAt: new Date(now - 20 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 20 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ] as Order[];
}

export class MockOrderService {
  async getUserOrders(): Promise<ApiResponse<Order[]>> {
    await delay(400);
    const userId = 'mock-user';
    initializeUserOrders(userId);
    return {
      data: MOCK_USER_ORDERS[userId] || [],
      message: 'Orders retrieved successfully',
    };
  }

  async getById(id: string): Promise<ApiResponse<Order>> {
    await delay(200);
    for (const orders of Object.values(MOCK_USER_ORDERS)) {
      const order = orders.find(o => o.id === id);
      if (order) {
        return { data: order, message: 'Order found' };
      }
    }
    throw new Error('Order not found');
  }

  async updateStatus(id: string, status: Order['status']): Promise<ApiResponse<Order>> {
    await delay(300);
    for (const orders of Object.values(MOCK_USER_ORDERS)) {
      const order = orders.find(o => o.id === id);
      if (order) {
        order.status = status;
        order.updatedAt = new Date().toISOString();
        return { data: order, message: 'Order status updated' };
      }
    }
    throw new Error('Order not found');
  }

  async cancel(id: string): Promise<ApiResponse<Order>> {
    await delay(300);
    for (const orders of Object.values(MOCK_USER_ORDERS)) {
      const order = orders.find(o => o.id === id);
      if (order) {
        order.status = 'cancelled';
        order.updatedAt = new Date().toISOString();
        return { data: order, message: 'Order cancelled' };
      }
    }
    throw new Error('Order not found');
  }

  async getBusinessOrders(businessId: string): Promise<ApiResponse<Order[]>> {
    await delay(400);
    const now = Date.now();
    const mockBusinessOrders: Order[] = [
      {
        id: `ord-biz-${generateId()}`,
        venueId: '2',
        venueName: 'Bella Italia Restaurant',
        userId: 'guest-1',
        items: [
          { id: '1', name: 'Margherita Pizza', quantity: 2, price: 18.99, total: 37.98 },
          { id: '2', name: 'Caesar Salad', quantity: 1, price: 12.50, total: 12.50 },
        ],
        subtotal: 50.48,
        tax: 4.54,
        total: 55.02,
        status: 'preparing',
        orderType: 'dine_in',
        createdAt: new Date(now - 15 * 60 * 1000).toISOString(),
        updatedAt: new Date(now - 5 * 60 * 1000).toISOString(),
      },
      {
        id: `ord-biz-${generateId()}`,
        venueId: '2',
        venueName: 'Bella Italia Restaurant',
        userId: 'guest-2',
        items: [
          { id: '1', name: 'Spaghetti Carbonara', quantity: 1, price: 22.00, total: 22.00 },
          { id: '2', name: 'Tiramisu', quantity: 1, price: 9.99, total: 9.99 },
          { id: '3', name: 'House Wine', quantity: 2, price: 8.00, total: 16.00 },
        ],
        subtotal: 47.99,
        tax: 4.32,
        total: 52.31,
        status: 'delivered',
        orderType: 'dine_in',
        createdAt: new Date(now - 2 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date(now - 1 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: `ord-biz-${generateId()}`,
        venueId: '2',
        venueName: 'Bella Italia Restaurant',
        userId: 'guest-3',
        items: [
          { id: '1', name: 'Lasagna', quantity: 1, price: 19.99, total: 19.99 },
        ],
        subtotal: 19.99,
        tax: 1.80,
        total: 21.79,
        status: 'ready',
        orderType: 'takeout',
        createdAt: new Date(now - 30 * 60 * 1000).toISOString(),
        updatedAt: new Date(now - 10 * 60 * 1000).toISOString(),
      },
      {
        id: `ord-biz-${generateId()}`,
        venueId: '2',
        venueName: 'Bella Italia Restaurant',
        userId: 'guest-4',
        items: [
          { id: '1', name: 'Bruschetta', quantity: 2, price: 10.99, total: 21.98 },
          { id: '2', name: 'Risotto', quantity: 2, price: 24.00, total: 48.00 },
          { id: '3', name: 'Gelato', quantity: 4, price: 6.50, total: 26.00 },
        ],
        subtotal: 95.98,
        tax: 8.64,
        total: 104.62,
        status: 'delivered',
        orderType: 'dine_in',
        createdAt: new Date(now - 4 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date(now - 3 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: `ord-biz-${generateId()}`,
        venueId: '2',
        venueName: 'Bella Italia Restaurant',
        userId: 'guest-5',
        items: [
          { id: '1', name: 'Caprese Salad', quantity: 1, price: 14.50, total: 14.50 },
        ],
        subtotal: 14.50,
        tax: 1.31,
        total: 15.81,
        status: 'cancelled',
        orderType: 'delivery',
        createdAt: new Date(now - 6 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date(now - 5 * 60 * 60 * 1000).toISOString(),
      },
    ] as Order[];
    
    return {
      data: mockBusinessOrders,
      message: 'Business orders retrieved',
    };
  }
}
