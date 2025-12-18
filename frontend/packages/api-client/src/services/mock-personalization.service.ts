/**
 * Mock Personalization Service
 * Provides mock preferences, interactions, and personalization data.
 */
import type { ApiResponse } from '@hospitality-platform/types';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const generateId = () => Math.random().toString(36).substr(2, 9);

// Types matching what the pages expect
interface GuestProfile {
  id: string;
  user_id: string;
  status: string;
  consentMarketing: boolean;
  consentAnalytics: boolean;
  created_at: string;
  updated_at: string;
}

interface GuestPreference {
  id: string;
  guest_id: string;
  key: string;
  value: any;
  category?: string;
  source: 'explicit' | 'inferred' | 'default';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface PreferenceCategory {
  id: string;
  key: string;
  name: string;
  description: string;
}

interface GuestInteraction {
  id: string;
  guest_id: string;
  interaction_type: string;
  entity_type?: string;
  entity_id?: string;
  metadata?: Record<string, any>;
  timestamp: string;
  created_at: string;
}

interface GuestSegment {
  id: string;
  segment_name: string;
  name: string;
  description: string;
  confidence: number;
}

interface BehaviorSignal {
  id: string;
  signal_type: string;
  description: string;
  confidence: number;
  detected_at: string;
}

interface PersonalizationContext {
  guest_id: string;
  preference_count: number;
  interaction_count: number;
  segment_count: number;
  last_updated: string;
}

// Storage
const MOCK_PROFILES: Record<string, GuestProfile> = {};
const MOCK_PREFERENCES: Record<string, GuestPreference[]> = {};
const MOCK_INTERACTIONS: Record<string, GuestInteraction[]> = {};
const MOCK_SEGMENTS: Record<string, GuestSegment[]> = {};
const MOCK_SIGNALS: Record<string, BehaviorSignal[]> = {};

const PREFERENCE_CATEGORIES: PreferenceCategory[] = [
  { id: '1', key: 'dining', name: 'Dining', description: 'Food and dining preferences' },
  { id: '2', key: 'accommodation', name: 'Accommodation', description: 'Room and stay preferences' },
  { id: '3', key: 'communication', name: 'Communication', description: 'Contact preferences' },
  { id: '4', key: 'activities', name: 'Activities', description: 'Activity and entertainment preferences' },
];

function initializeUserData(guestId: string) {
  if (MOCK_PROFILES[guestId]) return;

  const now = Date.now();

  // Create profile
  MOCK_PROFILES[guestId] = {
    id: `profile-${guestId}`,
    user_id: guestId,
    status: 'active',
    consentMarketing: true,
    consentAnalytics: true,
    created_at: new Date(now - 90 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(),
  };

  // Create preferences
  MOCK_PREFERENCES[guestId] = [
    {
      id: `pref-${generateId()}`,
      guest_id: guestId,
      key: 'dietary_restrictions',
      value: ['vegetarian', 'gluten-free'],
      category: 'dining',
      source: 'explicit',
      is_active: true,
      created_at: new Date(now - 60 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(now - 10 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `pref-${generateId()}`,
      guest_id: guestId,
      key: 'room_preferences',
      value: ['high_floor', 'quiet_room', 'king_bed'],
      category: 'accommodation',
      source: 'explicit',
      is_active: true,
      created_at: new Date(now - 45 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(now - 15 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `pref-${generateId()}`,
      guest_id: guestId,
      key: 'cuisine_types',
      value: ['italian', 'japanese', 'mediterranean'],
      category: 'dining',
      source: 'inferred',
      is_active: true,
      created_at: new Date(now - 30 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `pref-${generateId()}`,
      guest_id: guestId,
      key: 'communication_channel',
      value: 'email',
      category: 'communication',
      source: 'explicit',
      is_active: true,
      created_at: new Date(now - 90 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(now - 90 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `pref-${generateId()}`,
      guest_id: guestId,
      key: 'price_range',
      value: 'mid_to_high',
      category: 'accommodation',
      source: 'inferred',
      is_active: true,
      created_at: new Date(now - 20 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(now - 3 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `pref-${generateId()}`,
      guest_id: guestId,
      key: 'activity_interests',
      value: ['spa', 'fitness', 'fine_dining'],
      category: 'activities',
      source: 'inferred',
      is_active: true,
      created_at: new Date(now - 25 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(now - 7 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ];

  // Create interactions
  MOCK_INTERACTIONS[guestId] = [
    {
      id: `int-${generateId()}`,
      guest_id: guestId,
      interaction_type: 'booking_completed',
      entity_type: 'venue',
      entity_id: '1',
      metadata: { venue_name: 'The Grand Hotel', amount: 450 },
      timestamp: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(),
      created_at: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `int-${generateId()}`,
      guest_id: guestId,
      interaction_type: 'venue_viewed',
      entity_type: 'venue',
      entity_id: '2',
      metadata: { venue_name: 'Bella Italia Restaurant', duration_seconds: 120 },
      timestamp: new Date(now - 3 * 24 * 60 * 60 * 1000).toISOString(),
      created_at: new Date(now - 3 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `int-${generateId()}`,
      guest_id: guestId,
      interaction_type: 'search_performed',
      entity_type: 'search',
      metadata: { query: 'italian restaurant', filters: { cuisine: 'italian' } },
      timestamp: new Date(now - 3 * 24 * 60 * 60 * 1000).toISOString(),
      created_at: new Date(now - 3 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `int-${generateId()}`,
      guest_id: guestId,
      interaction_type: 'favorite_added',
      entity_type: 'venue',
      entity_id: '5',
      metadata: { venue_name: 'Sushi Master' },
      timestamp: new Date(now - 7 * 24 * 60 * 60 * 1000).toISOString(),
      created_at: new Date(now - 7 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `int-${generateId()}`,
      guest_id: guestId,
      interaction_type: 'review_submitted',
      entity_type: 'venue',
      entity_id: '2',
      metadata: { venue_name: 'Bella Italia Restaurant', rating: 5, comment: 'Excellent food!' },
      timestamp: new Date(now - 10 * 24 * 60 * 60 * 1000).toISOString(),
      created_at: new Date(now - 10 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `int-${generateId()}`,
      guest_id: guestId,
      interaction_type: 'order_completed',
      entity_type: 'order',
      entity_id: 'ord-123',
      metadata: { venue_name: 'Coffee Corner', total: 30.52 },
      timestamp: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(),
      created_at: new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `int-${generateId()}`,
      guest_id: guestId,
      interaction_type: 'loyalty_reward_redeemed',
      entity_type: 'loyalty',
      metadata: { reward_name: '15% Off Dining', points_spent: 250 },
      timestamp: new Date(now - 12 * 24 * 60 * 60 * 1000).toISOString(),
      created_at: new Date(now - 12 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ];

  // Create segments
  MOCK_SEGMENTS[guestId] = [
    {
      id: `seg-${generateId()}`,
      segment_name: 'frequent_traveler',
      name: 'Frequent Traveler',
      description: 'Books accommodations regularly',
      confidence: 0.85,
    },
    {
      id: `seg-${generateId()}`,
      segment_name: 'fine_dining_enthusiast',
      name: 'Fine Dining Enthusiast',
      description: 'Prefers upscale restaurants',
      confidence: 0.78,
    },
    {
      id: `seg-${generateId()}`,
      segment_name: 'health_conscious',
      name: 'Health Conscious',
      description: 'Prefers healthy and dietary-specific options',
      confidence: 0.72,
    },
    {
      id: `seg-${generateId()}`,
      segment_name: 'loyalty_engaged',
      name: 'Loyalty Program Engaged',
      description: 'Actively uses loyalty rewards',
      confidence: 0.91,
    },
  ];

  // Create behavior signals
  MOCK_SIGNALS[guestId] = [
    {
      id: `sig-${generateId()}`,
      signal_type: 'weekend_booker',
      description: 'Tends to make bookings for weekends',
      confidence: 0.82,
      detected_at: new Date(now - 15 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `sig-${generateId()}`,
      signal_type: 'advance_planner',
      description: 'Books well in advance (7+ days)',
      confidence: 0.75,
      detected_at: new Date(now - 20 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `sig-${generateId()}`,
      signal_type: 'evening_browser',
      description: 'Most active between 6PM-10PM',
      confidence: 0.68,
      detected_at: new Date(now - 10 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: `sig-${generateId()}`,
      signal_type: 'price_sensitive',
      description: 'Responds well to discounts and offers',
      confidence: 0.65,
      detected_at: new Date(now - 25 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ];
}

export class MockPersonalizationService {
  async getGuestProfile(guestId: string): Promise<ApiResponse<GuestProfile>> {
    await delay(300);
    initializeUserData(guestId);
    return { data: MOCK_PROFILES[guestId], message: 'Profile retrieved' };
  }

  async getCurrentGuestProfile(): Promise<ApiResponse<GuestProfile>> {
    await delay(300);
    const guestId = 'mock-user';
    initializeUserData(guestId);
    return { data: MOCK_PROFILES[guestId], message: 'Profile retrieved' };
  }

  async getGuestPreferences(guestId: string): Promise<ApiResponse<GuestPreference[]>> {
    await delay(300);
    initializeUserData(guestId);
    return { data: MOCK_PREFERENCES[guestId] || [], message: 'Preferences retrieved' };
  }

  async createPreference(guestId: string, data: any): Promise<ApiResponse<GuestPreference>> {
    await delay(300);
    initializeUserData(guestId);
    const newPref: GuestPreference = {
      id: `pref-${generateId()}`,
      guest_id: guestId,
      key: data.key,
      value: data.value,
      category: data.category,
      source: data.source || 'explicit',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    MOCK_PREFERENCES[guestId].push(newPref);
    return { data: newPref, message: 'Preference created' };
  }

  async getPreferenceCategories(): Promise<ApiResponse<PreferenceCategory[]>> {
    await delay(200);
    return { data: PREFERENCE_CATEGORIES, message: 'Categories retrieved' };
  }

  async getGuestInteractions(guestId: string, filters?: any): Promise<ApiResponse<GuestInteraction[]>> {
    await delay(400);
    initializeUserData(guestId);
    let interactions = MOCK_INTERACTIONS[guestId] || [];
    if (filters?.limit) {
      interactions = interactions.slice(0, filters.limit);
    }
    return { data: interactions, message: 'Interactions retrieved' };
  }

  async getPersonalizationContext(guestId: string): Promise<ApiResponse<PersonalizationContext>> {
    await delay(300);
    initializeUserData(guestId);
    return {
      data: {
        guest_id: guestId,
        preference_count: MOCK_PREFERENCES[guestId]?.length || 0,
        interaction_count: MOCK_INTERACTIONS[guestId]?.length || 0,
        segment_count: MOCK_SEGMENTS[guestId]?.length || 0,
        last_updated: new Date().toISOString(),
      },
      message: 'Context retrieved',
    };
  }

  async getGuestSegments(guestId: string): Promise<ApiResponse<GuestSegment[]>> {
    await delay(300);
    initializeUserData(guestId);
    return { data: MOCK_SEGMENTS[guestId] || [], message: 'Segments retrieved' };
  }

  async getBehaviorSignals(guestId: string): Promise<ApiResponse<BehaviorSignal[]>> {
    await delay(300);
    initializeUserData(guestId);
    return { data: MOCK_SIGNALS[guestId] || [], message: 'Signals retrieved' };
  }
}
