/**
 * Mock Business Services
 * Provides mock data for all business-related pages.
 */
import type { InventoryItem, ApiResponse } from '@hospitality-platform/types';
import type { PriceEstimateRequest, PriceEstimateResponse, PricingRule, BasePrice } from './pricing.service';
import type { Task, TaskListResponse, TaskFilters } from './housekeeping.service';
import type { FeedbackResponse, FeedbackListResponse, VenueInsights } from './feedback.service';
import type { Campaign, CampaignListResponse } from './campaigns.service';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
const generateId = () => Math.random().toString(36).substr(2, 9);

// ============ INVENTORY MOCK ============
const MOCK_INVENTORY: InventoryItem[] = [
  { id: '1', productName: 'Fresh Towels', currentStock: 250, lowStockThreshold: 50, unit: 'pieces', category: 'Linens', alerts: [] },
  { id: '2', productName: 'Shampoo Bottles', currentStock: 45, lowStockThreshold: 100, unit: 'bottles', category: 'Amenities', alerts: [{ type: 'low_stock', severity: 'warning', message: 'Stock below threshold' }] },
  { id: '3', productName: 'Toilet Paper Rolls', currentStock: 180, lowStockThreshold: 200, unit: 'rolls', category: 'Bathroom', alerts: [{ type: 'low_stock', severity: 'warning', message: 'Stock below threshold' }] },
  { id: '4', productName: 'Pillow Cases', currentStock: 120, lowStockThreshold: 40, unit: 'pieces', category: 'Linens', alerts: [] },
  { id: '5', productName: 'Coffee Pods', currentStock: 500, lowStockThreshold: 100, unit: 'pods', category: 'Beverages', alerts: [] },
  { id: '6', productName: 'Hand Soap', currentStock: 15, lowStockThreshold: 50, unit: 'bottles', category: 'Amenities', alerts: [{ type: 'low_stock', severity: 'error', message: 'Critical stock level' }] },
  { id: '7', productName: 'Bed Sheets (King)', currentStock: 80, lowStockThreshold: 30, unit: 'sets', category: 'Linens', alerts: [] },
  { id: '8', productName: 'Mini Bar Snacks', currentStock: 200, lowStockThreshold: 50, unit: 'items', category: 'Food', alerts: [] },
] as InventoryItem[];

export class MockInventoryService {
  async getInventory(businessId: string): Promise<ApiResponse<InventoryItem[]>> {
    await delay(400);
    return { data: MOCK_INVENTORY, message: 'Inventory retrieved' };
  }

  async updateStock(itemId: string, quantity: number): Promise<ApiResponse<InventoryItem>> {
    await delay(300);
    const item = MOCK_INVENTORY.find(i => i.id === itemId);
    if (item) {
      item.currentStock = quantity;
      item.alerts = quantity < item.lowStockThreshold ? [{ type: 'low_stock', severity: 'warning', message: 'Stock below threshold' }] : [];
    }
    return { data: item!, message: 'Stock updated' };
  }

  async getLowStockItems(businessId: string): Promise<ApiResponse<InventoryItem[]>> {
    await delay(300);
    return { data: MOCK_INVENTORY.filter(i => i.alerts.length > 0), message: 'Low stock items retrieved' };
  }
}

// ============ PRICING MOCK ============
const MOCK_PRICING_RULES: PricingRule[] = [
  { id: '1', name: 'Weekend Premium', rule_type: 'time_based', is_active: true, priority: 1, multiplier_min: 1.2, multiplier_max: 1.5, conditions: { days: ['saturday', 'sunday'] }, created_at: new Date().toISOString() },
  { id: '2', name: 'High Demand Surge', rule_type: 'demand_based', is_active: true, priority: 2, multiplier_min: 1.1, multiplier_max: 1.8, conditions: { occupancy_threshold: 80 }, created_at: new Date().toISOString() },
  { id: '3', name: 'Holiday Special', rule_type: 'event_based', is_active: true, priority: 3, multiplier_min: 1.3, multiplier_max: 2.0, conditions: { events: ['christmas', 'new_year'] }, created_at: new Date().toISOString() },
  { id: '4', name: 'Summer Season', rule_type: 'seasonal', is_active: false, priority: 4, multiplier_min: 1.1, multiplier_max: 1.4, conditions: { months: [6, 7, 8] }, created_at: new Date().toISOString() },
];

const MOCK_BASE_PRICES: BasePrice[] = [
  { id: '1', venue_id: 'demo', venue_type: 'hotel', item_category: 'Standard Room', base_price: 150, currency: 'USD', effective_from: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '2', venue_id: 'demo', venue_type: 'hotel', item_category: 'Deluxe Room', base_price: 250, currency: 'USD', effective_from: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '3', venue_id: 'demo', venue_type: 'hotel', item_category: 'Suite', base_price: 450, currency: 'USD', effective_from: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '4', venue_id: 'demo', venue_type: 'restaurant', item_category: 'Dinner', base_price: 75, currency: 'USD', effective_from: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString() },
];

export class MockPricingService {
  async getPriceEstimate(request: PriceEstimateRequest): Promise<PriceEstimateResponse> {
    await delay(500);
    const date = new Date(request.booking_time);
    const isWeekend = date.getDay() === 0 || date.getDay() === 6;
    const hour = date.getHours();
    const isPeak = (hour >= 18 && hour <= 21) || isWeekend;
    const demandLevels = ['very_low', 'low', 'normal', 'high', 'very_high'] as const;
    const demandLevel = isPeak ? demandLevels[3 + Math.floor(Math.random() * 2)] : demandLevels[1 + Math.floor(Math.random() * 2)];
    const basePrice = request.venue_type === 'hotel' ? 200 : 50;
    const multiplier = isPeak ? 1.3 : 1.0;

    return {
      venue_id: request.venue_id,
      estimated_price: Math.round(basePrice * multiplier * (request.party_size || 1)),
      currency: 'USD',
      demand_level: demandLevel,
      is_peak_time: isPeak,
      price_factors: isPeak ? ['Weekend Premium', 'Peak Hours'] : ['Standard Rate'],
      valid_until: new Date(Date.now() + 30 * 60 * 1000).toISOString(),
    };
  }

  async listRules(venueId?: string): Promise<PricingRule[]> {
    await delay(300);
    return MOCK_PRICING_RULES;
  }

  async listBasePrices(venueId: string): Promise<BasePrice[]> {
    await delay(300);
    return MOCK_BASE_PRICES;
  }
}

// ============ HOUSEKEEPING/TASKS MOCK ============
const now = Date.now();
const MOCK_TASKS: Task[] = [
  { id: '1', reference: 'TSK-001', task_type: 'cleaning', status: 'in_progress', priority: 'high', venue_id: 'demo', room_number: '301', floor_number: 3, description: 'Deep cleaning required', assigned_staff_id: 'staff-1', assigned_staff_name: 'Maria Garcia', is_vip: true, scheduled_start: new Date(now - 1 * 60 * 60 * 1000).toISOString(), created_at: new Date(now - 2 * 60 * 60 * 1000).toISOString(), updated_at: new Date(now - 30 * 60 * 1000).toISOString() },
  { id: '2', reference: 'TSK-002', task_type: 'maintenance', status: 'pending', priority: 'urgent', venue_id: 'demo', room_number: '205', floor_number: 2, description: 'AC not working', is_vip: false, scheduled_start: new Date(now).toISOString(), created_at: new Date(now - 1 * 60 * 60 * 1000).toISOString(), updated_at: new Date(now - 1 * 60 * 60 * 1000).toISOString() },
  { id: '3', reference: 'TSK-003', task_type: 'restocking', status: 'assigned', priority: 'medium', venue_id: 'demo', room_number: '412', floor_number: 4, description: 'Mini bar refill', assigned_staff_id: 'staff-2', assigned_staff_name: 'John Smith', is_vip: false, scheduled_start: new Date(now + 1 * 60 * 60 * 1000).toISOString(), created_at: new Date(now - 3 * 60 * 60 * 1000).toISOString(), updated_at: new Date(now - 2 * 60 * 60 * 1000).toISOString() },
  { id: '4', reference: 'TSK-004', task_type: 'turndown', status: 'completed', priority: 'low', venue_id: 'demo', room_number: '508', floor_number: 5, assigned_staff_id: 'staff-1', assigned_staff_name: 'Maria Garcia', is_vip: true, scheduled_start: new Date(now - 4 * 60 * 60 * 1000).toISOString(), actual_end: new Date(now - 3 * 60 * 60 * 1000).toISOString(), created_at: new Date(now - 6 * 60 * 60 * 1000).toISOString(), updated_at: new Date(now - 3 * 60 * 60 * 1000).toISOString() },
  { id: '5', reference: 'TSK-005', task_type: 'inspection', status: 'delayed', priority: 'high', venue_id: 'demo', floor_number: 2, description: 'Fire safety inspection', delay_reason: 'Waiting for fire marshal', is_vip: false, scheduled_start: new Date(now - 2 * 60 * 60 * 1000).toISOString(), created_at: new Date(now - 24 * 60 * 60 * 1000).toISOString(), updated_at: new Date(now - 1 * 60 * 60 * 1000).toISOString() },
  { id: '6', reference: 'TSK-006', task_type: 'cleaning', status: 'pending', priority: 'medium', venue_id: 'demo', room_number: '102', floor_number: 1, description: 'Checkout cleaning', is_vip: false, scheduled_start: new Date(now + 2 * 60 * 60 * 1000).toISOString(), created_at: new Date(now - 30 * 60 * 1000).toISOString(), updated_at: new Date(now - 30 * 60 * 1000).toISOString() },
  { id: '7', reference: 'TSK-007', task_type: 'maintenance', status: 'completed', priority: 'low', venue_id: 'demo', room_number: '315', floor_number: 3, description: 'Light bulb replacement', assigned_staff_id: 'staff-3', assigned_staff_name: 'Mike Johnson', is_vip: false, actual_end: new Date(now - 5 * 60 * 60 * 1000).toISOString(), created_at: new Date(now - 8 * 60 * 60 * 1000).toISOString(), updated_at: new Date(now - 5 * 60 * 60 * 1000).toISOString() },
  { id: '8', reference: 'TSK-008', task_type: 'restocking', status: 'in_progress', priority: 'medium', venue_id: 'demo', floor_number: 4, description: 'Hallway supplies', assigned_staff_id: 'staff-2', assigned_staff_name: 'John Smith', is_vip: false, scheduled_start: new Date(now - 30 * 60 * 1000).toISOString(), actual_start: new Date(now - 15 * 60 * 1000).toISOString(), created_at: new Date(now - 2 * 60 * 60 * 1000).toISOString(), updated_at: new Date(now - 15 * 60 * 1000).toISOString() },
];

export class MockHousekeepingService {
  async listTasks(filters?: TaskFilters): Promise<TaskListResponse> {
    await delay(400);
    let tasks = [...MOCK_TASKS];
    if (filters?.statuses?.length) tasks = tasks.filter(t => filters.statuses!.includes(t.status));
    if (filters?.task_types?.length) tasks = tasks.filter(t => filters.task_types!.includes(t.task_type));
    return { tasks, total: tasks.length, page: 1, page_size: 20, total_pages: 1 };
  }

  async getPendingTasks(limit = 50): Promise<Task[]> {
    await delay(300);
    return MOCK_TASKS.filter(t => t.status === 'pending' || t.status === 'assigned').slice(0, limit);
  }

  async getOverdueTasks(): Promise<Task[]> {
    await delay(300);
    return MOCK_TASKS.filter(t => t.status === 'delayed');
  }

  async startTask(taskId: string): Promise<Task> {
    await delay(300);
    const task = MOCK_TASKS.find(t => t.id === taskId);
    if (task) { task.status = 'in_progress'; task.actual_start = new Date().toISOString(); }
    return task!;
  }

  async completeTask(taskId: string): Promise<Task> {
    await delay(300);
    const task = MOCK_TASKS.find(t => t.id === taskId);
    if (task) { task.status = 'completed'; task.actual_end = new Date().toISOString(); }
    return task!;
  }
}

// ============ FEEDBACK MOCK ============
const MOCK_FEEDBACK: FeedbackResponse[] = [
  { id: '1', feedback_reference: 'FB-001', venue_id: 'demo', category: 'service', rating: 5, comment: 'Exceptional service! The staff went above and beyond.', status: 'analyzed', sentiment: { sentiment: 'positive', confidence: 0.95, key_phrases: ['exceptional service', 'above and beyond'] }, created_at: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '2', feedback_reference: 'FB-002', venue_id: 'demo', category: 'food', rating: 4, comment: 'Great breakfast buffet, would love more vegan options.', status: 'analyzed', sentiment: { sentiment: 'positive', confidence: 0.82, key_phrases: ['great breakfast', 'vegan options'] }, created_at: new Date(now - 2 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '3', feedback_reference: 'FB-003', venue_id: 'demo', category: 'cleanliness', rating: 3, comment: 'Room was okay, bathroom could have been cleaner.', status: 'reviewed', sentiment: { sentiment: 'neutral', confidence: 0.75, key_phrases: ['okay', 'cleaner'] }, created_at: new Date(now - 3 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '4', feedback_reference: 'FB-004', venue_id: 'demo', category: 'value', rating: 2, comment: 'Overpriced for what you get. Expected more amenities.', status: 'analyzed', sentiment: { sentiment: 'negative', confidence: 0.88, key_phrases: ['overpriced', 'expected more'] }, created_at: new Date(now - 4 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '5', feedback_reference: 'FB-005', venue_id: 'demo', category: 'ambiance', rating: 5, comment: 'Beautiful decor and very relaxing atmosphere.', status: 'analyzed', sentiment: { sentiment: 'positive', confidence: 0.92, key_phrases: ['beautiful decor', 'relaxing atmosphere'] }, created_at: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '6', feedback_reference: 'FB-006', venue_id: 'demo', category: 'overall', rating: 4, comment: 'Great stay overall. Will definitely come back!', status: 'pending', sentiment: { sentiment: 'positive', confidence: 0.90, key_phrases: ['great stay', 'come back'] }, created_at: new Date(now - 6 * 24 * 60 * 60 * 1000).toISOString() },
];

const MOCK_VENUE_INSIGHTS: VenueInsights = {
  venue_id: 'demo',
  total_feedback: 89,
  average_rating: 4.2,
  sentiment_distribution: { positive: 0.65, neutral: 0.22, negative: 0.13 },
  vs_platform_average: 0.08,
  top_positive_topics: ['Friendly staff', 'Clean rooms', 'Great location', 'Comfortable beds'],
  areas_for_improvement: ['WiFi speed', 'Parking availability', 'Room service timing'],
};

export class MockFeedbackService {
  async listFeedback(params?: { venue_id?: string; status?: string; page?: number; page_size?: number }): Promise<FeedbackListResponse> {
    await delay(400);
    let items = [...MOCK_FEEDBACK];
    if (params?.status && params.status !== 'all') items = items.filter(f => f.status === params.status);
    return { items, total: items.length, page: 1, page_size: 20, has_more: false };
  }

  async getVenueInsights(venueId: string): Promise<VenueInsights> {
    await delay(400);
    return MOCK_VENUE_INSIGHTS;
  }
}

// ============ CAMPAIGNS MOCK ============
const MOCK_CAMPAIGNS: Campaign[] = [
  { id: '1', name: 'Winter Getaway Sale', description: '20% off all bookings this winter season', campaign_type: 'discount', status: 'active', start_date: new Date(now - 15 * 24 * 60 * 60 * 1000).toISOString(), end_date: new Date(now + 45 * 24 * 60 * 60 * 1000).toISOString(), discount_percentage: 20, max_uses: 500, current_uses: 127, created_at: new Date(now - 20 * 24 * 60 * 60 * 1000).toISOString(), updated_at: new Date(now - 15 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '2', name: 'Double Points Weekend', description: 'Earn 2x loyalty points on weekend stays', campaign_type: 'points_multiplier', status: 'active', start_date: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(), end_date: new Date(now + 25 * 24 * 60 * 60 * 1000).toISOString(), points_multiplier: 2, max_uses: 1000, current_uses: 234, created_at: new Date(now - 10 * 24 * 60 * 60 * 1000).toISOString(), updated_at: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '3', name: 'New Year Bonus', description: '500 bonus points for bookings in January', campaign_type: 'bonus_points', status: 'scheduled', start_date: new Date(now + 15 * 24 * 60 * 60 * 1000).toISOString(), end_date: new Date(now + 45 * 24 * 60 * 60 * 1000).toISOString(), bonus_points: 500, created_at: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(), updated_at: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '4', name: 'Free Breakfast Deal', description: 'Complimentary breakfast with 2+ night stays', campaign_type: 'free_item', status: 'draft', start_date: new Date(now + 30 * 24 * 60 * 60 * 1000).toISOString(), end_date: new Date(now + 90 * 24 * 60 * 60 * 1000).toISOString(), min_purchase: 200, created_at: new Date(now - 2 * 24 * 60 * 60 * 1000).toISOString(), updated_at: new Date(now - 2 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '5', name: 'Summer Flash Sale', description: '15% off summer bookings - limited time!', campaign_type: 'discount', status: 'completed', start_date: new Date(now - 120 * 24 * 60 * 60 * 1000).toISOString(), end_date: new Date(now - 60 * 24 * 60 * 60 * 1000).toISOString(), discount_percentage: 15, max_uses: 300, current_uses: 300, created_at: new Date(now - 150 * 24 * 60 * 60 * 1000).toISOString(), updated_at: new Date(now - 60 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '6', name: 'VIP Member Exclusive', description: '25% off for gold tier members', campaign_type: 'discount', status: 'paused', start_date: new Date(now - 30 * 24 * 60 * 60 * 1000).toISOString(), end_date: new Date(now + 60 * 24 * 60 * 60 * 1000).toISOString(), discount_percentage: 25, target_audience: 'gold_members', max_uses: 200, current_uses: 45, created_at: new Date(now - 35 * 24 * 60 * 60 * 1000).toISOString(), updated_at: new Date(now - 10 * 24 * 60 * 60 * 1000).toISOString() },
];

export class MockCampaignsService {
  async listCampaigns(params?: { status?: string; venue_id?: string; page?: number; page_size?: number }): Promise<CampaignListResponse> {
    await delay(400);
    let items = [...MOCK_CAMPAIGNS];
    if (params?.status && params.status !== 'all') items = items.filter(c => c.status === params.status);
    return { items, total: items.length, page: 1, page_size: 50 };
  }

  async getActiveCampaigns(venueId?: string): Promise<Campaign[]> {
    await delay(300);
    return MOCK_CAMPAIGNS.filter(c => c.status === 'active');
  }

  async createCampaign(data: any): Promise<Campaign> {
    await delay(400);
    const campaign: Campaign = { id: generateId(), ...data, status: 'draft', current_uses: 0, created_at: new Date().toISOString(), updated_at: new Date().toISOString() };
    MOCK_CAMPAIGNS.push(campaign);
    return campaign;
  }

  async activateCampaign(campaignId: string): Promise<Campaign> {
    await delay(300);
    const campaign = MOCK_CAMPAIGNS.find(c => c.id === campaignId);
    if (campaign) { campaign.status = 'active'; campaign.updated_at = new Date().toISOString(); }
    return campaign!;
  }

  async pauseCampaign(campaignId: string): Promise<Campaign> {
    await delay(300);
    const campaign = MOCK_CAMPAIGNS.find(c => c.id === campaignId);
    if (campaign) { campaign.status = 'paused'; campaign.updated_at = new Date().toISOString(); }
    return campaign!;
  }
}
