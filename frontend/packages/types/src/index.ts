// User Types
export interface User {
  id: string;
  email: string;
  name: string;
  phone?: string;
  roles: UserRole[];
  preferences: UserPreferences;
  createdAt: string;
  updatedAt: string;
}

export type UserRole = 'guest' | 'business' | 'admin';

export interface UserPreferences {
  dietaryRestrictions?: string[];
  favoriteCategories?: string[];
  notificationPreferences: NotificationPreferences;
  personalizationEnabled: boolean;
}

export interface NotificationPreferences {
  email: boolean;
  push: boolean;
  sms: boolean;
  marketing: boolean;
}

// Authentication
export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  phone?: string;
}

// Venue Types
export interface Venue {
  id: string;
  name: string;
  type: VenueType;
  description: string;
  address: Address;
  contact: ContactInfo;
  images: string[];
  rating: number;
  reviewCount: number;
  priceRange: PriceRange;
  amenities: string[];
  openingHours: OpeningHours;
  isAvailable: boolean;
  businessId: string;
  createdAt: string;
  updatedAt: string;
}

export type VenueType = 'hotel' | 'restaurant' | 'cafe' | 'retail';

export interface Address {
  street: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
}

export interface ContactInfo {
  phone?: string;
  email?: string;
  website?: string;
}

export type PriceRange = '$' | '$$' | '$$$' | '$$$$';

export interface OpeningHours {
  [key: string]: {
    open: string;
    close: string;
    isClosed?: boolean;
  };
}

// Booking Types
export interface Booking {
  id: string;
  venueId: string;
  venueName: string;
  userId: string;
  date: string;
  time: string;
  partySize: number;
  status: BookingStatus;
  specialRequests?: string;
  createdAt: string;
  updatedAt: string;
}

export type BookingStatus = 'pending' | 'confirmed' | 'cancelled' | 'completed' | 'no-show';

export interface CreateBookingRequest {
  venueId: string;
  date: string;
  time: string;
  partySize: number;
  specialRequests?: string;
}

// Order Types
export interface Order {
  id: string;
  venueId: string;
  venueName: string;
  userId: string;
  items: OrderItem[];
  subtotal: number;
  tax: number;
  tip?: number;
  total: number;
  status: OrderStatus;
  deliveryAddress?: Address;
  estimatedReadyTime?: string;
  createdAt: string;
  updatedAt: string;
}

export interface OrderItem {
  id: string;
  productId: string;
  name: string;
  quantity: number;
  price: number;
  customizations?: OrderItemCustomization[];
}

export interface OrderItemCustomization {
  optionId: string;
  optionName: string;
  value: string;
  priceModifier?: number;
}

export type OrderStatus = 'pending' | 'confirmed' | 'preparing' | 'ready' | 'out-for-delivery' | 'delivered' | 'cancelled';

export interface CreateOrderRequest {
  venueId: string;
  items: CreateOrderItem[];
  deliveryAddress?: Address;
  tip?: number;
}

export interface CreateOrderItem {
  productId: string;
  quantity: number;
  customizations?: OrderItemCustomization[];
}

// Product Types
export interface Product {
  id: string;
  venueId: string;
  name: string;
  description: string;
  category: string;
  price: number;
  images: string[];
  isAvailable: boolean;
  inventory?: InventoryInfo;
  customizations?: ProductCustomization[];
  dietaryInfo?: DietaryInfo;
}

export interface InventoryInfo {
  currentStock: number;
  lowStockThreshold: number;
  unit: string;
}

export interface ProductCustomization {
  id: string;
  name: string;
  type: 'single' | 'multiple';
  required: boolean;
  options: CustomizationOption[];
}

export interface CustomizationOption {
  id: string;
  name: string;
  priceModifier?: number;
}

export interface DietaryInfo {
  allergens?: string[];
  dietaryTags?: string[];
  calories?: number;
}

// Inventory Types
export interface InventoryItem {
  id: string;
  productId: string;
  productName: string;
  currentStock: number;
  lowStockThreshold: number;
  unit: string;
  lastUpdated: string;
  alerts: InventoryAlert[];
}

export interface InventoryAlert {
  type: 'low_stock' | 'out_of_stock' | 'overstock';
  message: string;
  severity: 'warning' | 'error' | 'info';
}

// Payment Types
export interface Payment {
  id: string;
  orderId?: string;
  bookingId?: string;
  amount: number;
  currency: string;
  status: PaymentStatus;
  method: PaymentMethod;
  transactionId?: string;
  processedAt?: string;
  failureReason?: string;
}

export type PaymentStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'refunded';

export type PaymentMethod = 'card' | 'digital_wallet' | 'bank_transfer';

export interface PaymentIntent {
  id: string;
  amount: number;
  currency: string;
  clientSecret: string;
}

// Review & Feedback Types
export interface Review {
  id: string;
  venueId: string;
  userId: string;
  userName: string;
  rating: number;
  comment: string;
  sentiment?: SentimentAnalysis;
  createdAt: string;
  updatedAt: string;
}

export interface SentimentAnalysis {
  label: 'positive' | 'neutral' | 'negative';
  score: number;
  processedAt: string;
}

export interface CreateReviewRequest {
  venueId: string;
  rating: number;
  comment: string;
}

// Analytics Types
export interface BusinessMetrics {
  revenue: RevenueMetrics;
  bookings: BookingMetrics;
  orders: OrderMetrics;
  customers: CustomerMetrics;
  sentiment: SentimentMetrics;
  period: DateRange;
}

export interface RevenueMetrics {
  total: number;
  change: number;
  changePercent: number;
  byPeriod: TimeSeriesData[];
}

export interface BookingMetrics {
  total: number;
  confirmed: number;
  cancelled: number;
  occupancyRate: number;
  averagePartySize: number;
  byPeriod: TimeSeriesData[];
}

export interface OrderMetrics {
  total: number;
  averageOrderValue: number;
  itemsSold: number;
  byPeriod: TimeSeriesData[];
}

export interface CustomerMetrics {
  total: number;
  new: number;
  returning: number;
  averageLifetimeValue: number;
}

export interface SentimentMetrics {
  positive: number;
  neutral: number;
  negative: number;
  averageScore: number;
  trend: 'improving' | 'declining' | 'stable';
}

export interface TimeSeriesData {
  date: string;
  value: number;
}

export interface DateRange {
  start: string;
  end: string;
}

// Recommendation Types
export interface Recommendation {
  id: string;
  venueId: string;
  venue: Venue;
  reason: string;
  confidence: number;
  category: 'personalized' | 'trending' | 'similar' | 'nearby';
}

// Pricing Types
export interface PricingRule {
  id: string;
  venueId: string;
  name: string;
  type: 'static' | 'dynamic' | 'promotional';
  conditions: PricingCondition[];
  adjustments: PricingAdjustment[];
  isActive: boolean;
  validFrom: string;
  validTo?: string;
}

export interface PricingCondition {
  field: string;
  operator: 'equals' | 'greater_than' | 'less_than' | 'between' | 'in';
  value: any;
}

export interface PricingAdjustment {
  type: 'percentage' | 'fixed';
  value: number;
  direction: 'increase' | 'decrease';
}

// Staff Types
export interface StaffMember {
  id: string;
  businessId: string;
  userId: string;
  name: string;
  email: string;
  role: StaffRole;
  permissions: Permission[];
  isActive: boolean;
  createdAt: string;
}

export type StaffRole = 'owner' | 'manager' | 'staff';

export type Permission = 
  | 'inventory:read' | 'inventory:write'
  | 'bookings:read' | 'bookings:write'
  | 'orders:read' | 'orders:write'
  | 'pricing:read' | 'pricing:write'
  | 'analytics:read'
  | 'staff:read' | 'staff:write'
  | 'settings:read' | 'settings:write';

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  meta?: ResponseMeta;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: Pagination;
  meta?: ResponseMeta;
}

export interface Pagination {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

export interface ResponseMeta {
  timestamp: string;
  requestId: string;
}

export interface ApiError {
  message: string;
  code: string;
  statusCode: number;
  details?: Record<string, any>;
  requestId?: string;
}

// Business Context Types
export interface BusinessContext {
  businessId: string;
  businessName: string;
  type: VenueType;
  locations: BusinessLocation[];
  currentLocationId?: string;
}

export interface BusinessLocation {
  id: string;
  name: string;
  address: Address;
  venueId: string;
}

// WebSocket Event Types
export interface WebSocketEvent {
  type: string;
  payload: any;
  timestamp: string;
}

export interface OrderStatusUpdateEvent extends WebSocketEvent {
  type: 'order.status.update';
  payload: {
    orderId: string;
    status: OrderStatus;
    estimatedReadyTime?: string;
  };
}

export interface InventoryUpdateEvent extends WebSocketEvent {
  type: 'inventory.update';
  payload: {
    productId: string;
    currentStock: number;
  };
}

export interface BookingUpdateEvent extends WebSocketEvent {
  type: 'booking.update';
  payload: {
    bookingId: string;
    status: BookingStatus;
  };
}

// Search & Filter Types
export interface SearchFilters {
  query?: string;
  venueTypes?: VenueType[];
  priceRange?: PriceRange[];
  location?: {
    lat: number;
    lng: number;
    radius?: number;
  };
  rating?: number;
  amenities?: string[];
  availability?: {
    date: string;
    time?: string;
  };
}

export interface SearchResult {
  venues: Venue[];
  total: number;
  filters: SearchFilters;
}

// Guest Interaction & Personalization Types
export interface GuestProfile {
  id: string;
  email?: string;
  name?: string;
  phone?: string;
  status: 'active' | 'inactive' | 'deleted' | 'anonymized';
  isAnonymous: boolean;
  consentMarketing: boolean;
  consentAnalytics: boolean;
  consentPersonalization: boolean;
  createdAt: string;
  updatedAt: string;
  lastInteractionAt?: string;
}

export interface GuestPreference {
  id: string;
  guestId: string;
  categoryId: string;
  category?: PreferenceCategory;
  key: string;
  value: any;
  valueType: 'string' | 'array' | 'boolean' | 'number' | 'object';
  source: 'explicit' | 'implicit' | 'inferred' | 'system';
  confidence: number;
  isActive: boolean;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface PreferenceCategory {
  id: string;
  name: string;
  description?: string;
  isSystem: boolean;
  createdAt: string;
}

export interface PreferenceHistory {
  id: string;
  preferenceId: string;
  oldValue?: any;
  newValue: any;
  changeReason?: string;
  changedAt: string;
  changedBy?: string;
}

export interface GuestInteraction {
  id: string;
  guestId: string;
  interactionTypeId: string;
  interactionType?: InteractionType;
  entityType?: string;
  entityId?: string;
  context?: Record<string, any>;
  interactionMetadata?: Record<string, any>;
  source: string;
  sourceEventId?: string;
  occurredAt: string;
  createdAt: string;
}

export interface InteractionType {
  id: string;
  name: string;
  description?: string;
  category: string;
  isSystem: boolean;
  createdAt: string;
}

export interface GuestSegment {
  id: string;
  guestId: string;
  segmentName: string;
  segmentCategory?: string;
  confidence: number;
  assignedAt: string;
  assignedBy: string;
  isActive: boolean;
}

export interface BehaviorSignal {
  id: string;
  guestId: string;
  signalType: string;
  signalName: string;
  signalValue: any;
  strength: number;
  computedAt: string;
  computedBy: string;
  isActive: boolean;
}

export interface PersonalizationContext {
  id: string;
  guestId: string;
  preferenceVector?: Record<string, any>;
  behaviorSummary?: Record<string, any>;
  segments?: string[];
  signals?: Array<{
    type: string;
    name: string;
    value: any;
    strength: number;
  }>;
  version: number;
  computedAt: string;
  computedBy: string;
}

export interface GuestDataExport {
  guest: GuestProfile;
  preferences: Array<{
    id: string;
    key: string;
    value: any;
    valueType: string;
    source: string;
    confidence: number;
    isActive: boolean;
    createdAt: string;
    updatedAt: string;
  }>;
  interactions: Array<{
    id: string;
    interactionType: string;
    entityType?: string;
    entityId?: string;
    context?: Record<string, any>;
    occurredAt: string;
  }>;
  segments: Array<{
    id: string;
    segmentName: string;
    segmentCategory?: string;
    confidence: number;
    assignedAt: string;
    isActive: boolean;
  }>;
  behaviorSignals: Array<{
    id: string;
    signalType: string;
    signalName: string;
    signalValue: any;
    strength: number;
    computedAt: string;
    isActive: boolean;
  }>;
  exportedAt: string;
}

export interface CreateGuestRequest {
  email?: string;
  name?: string;
  phone?: string;
  isAnonymous?: boolean;
  consentMarketing?: boolean;
  consentAnalytics?: boolean;
  consentPersonalization?: boolean;
}

export interface UpdateGuestRequest {
  email?: string;
  name?: string;
  phone?: string;
  consentMarketing?: boolean;
  consentAnalytics?: boolean;
  consentPersonalization?: boolean;
}

export interface CreatePreferenceRequest {
  categoryId: string;
  key: string;
  value: any;
  valueType: 'string' | 'array' | 'boolean' | 'number' | 'object';
  source?: 'explicit' | 'implicit' | 'inferred' | 'system';
  confidence?: number;
}

export interface UpdatePreferenceRequest {
  value?: any;
  valueType?: 'string' | 'array' | 'boolean' | 'number' | 'object';
  confidence?: number;
  isActive?: boolean;
  changeReason?: string;
}

export interface CreateInteractionRequest {
  interactionTypeId: string;
  entityType?: string;
  entityId?: string;
  context?: Record<string, any>;
  interactionMetadata?: Record<string, any>;
  source?: string;
  sourceEventId?: string;
  occurredAt?: string;
}

export interface InteractionFilter {
  interactionTypeId?: string;
  entityType?: string;
  entityId?: string;
  source?: string;
  startDate?: string;
  endDate?: string;
  limit?: number;
  offset?: number;
}

export interface ConsentPreferences {
  consentMarketing: boolean;
  consentAnalytics: boolean;
  consentPersonalization: boolean;
}

