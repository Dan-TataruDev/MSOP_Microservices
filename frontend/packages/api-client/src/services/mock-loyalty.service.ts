/**
 * Mock Loyalty Service
 * Provides mock loyalty/rewards data for development when the real API is not available.
 */
import type { LoyaltyMember, PointsHistoryResponse, PointsTransaction, Offer, LoyaltyTier } from './loyalty.service';

// Simulated delay for realistic UX
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Mock loyalty member data (stored in memory, persists during session)
let mockMemberData: Record<string, LoyaltyMember> = {};

function getOrCreateMember(guestId: string): LoyaltyMember {
  if (!mockMemberData[guestId]) {
    const tiers: LoyaltyTier[] = ['bronze', 'silver', 'gold', 'platinum'];
    const randomTier = tiers[Math.floor(Math.random() * 3)]; // Random tier, favor lower
    const tierIndex = tiers.indexOf(randomTier);
    
    const pointsBalance = 500 + Math.floor(Math.random() * 2000);
    const lifetimePoints = pointsBalance + Math.floor(Math.random() * 5000);
    
    mockMemberData[guestId] = {
      id: `loyalty-${guestId}`,
      guest_id: guestId,
      program_id: 'main-program',
      tier: randomTier,
      points_balance: pointsBalance,
      lifetime_points: lifetimePoints,
      next_tier: tierIndex < 3 ? tiers[tierIndex + 1] : undefined,
      points_to_next_tier: tierIndex < 3 ? 1000 + Math.floor(Math.random() * 2000) : undefined,
      joined_at: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
    };
  }
  return mockMemberData[guestId];
}

// Mock points history
const MOCK_TRANSACTION_DESCRIPTIONS = [
  { description: 'Stay at The Grand Hotel', points: 250, type: 'booking' },
  { description: 'Dinner at Bella Italia', points: 75, type: 'order' },
  { description: 'Welcome bonus', points: 100, type: 'bonus' },
  { description: 'Referral reward', points: 200, type: 'referral' },
  { description: 'Birthday bonus', points: 150, type: 'bonus' },
  { description: 'Coffee at Corner Cafe', points: 15, type: 'order' },
  { description: 'Spa treatment', points: 120, type: 'booking' },
  { description: 'Room upgrade purchase', points: -500, type: 'redemption' },
  { description: 'Weekend getaway booking', points: 350, type: 'booking' },
  { description: 'Loyalty tier bonus', points: 300, type: 'bonus' },
  { description: 'Free dessert redemption', points: -100, type: 'redemption' },
  { description: 'Survey completion', points: 25, type: 'bonus' },
  { description: 'Early check-in reward', points: 50, type: 'bonus' },
  { description: 'Room service order', points: 45, type: 'order' },
  { description: 'Gym session', points: 20, type: 'activity' },
];

function generatePointsHistory(guestId: string, limit: number): PointsTransaction[] {
  const transactions: PointsTransaction[] = [];
  const now = Date.now();
  
  for (let i = 0; i < limit; i++) {
    const template = MOCK_TRANSACTION_DESCRIPTIONS[Math.floor(Math.random() * MOCK_TRANSACTION_DESCRIPTIONS.length)];
    const daysAgo = Math.floor(Math.random() * 90);
    
    transactions.push({
      id: `txn-${guestId}-${i}`,
      points: template.points,
      description: template.description,
      source_type: template.type,
      source_id: `src-${i}`,
      created_at: new Date(now - daysAgo * 24 * 60 * 60 * 1000).toISOString(),
    });
  }
  
  // Sort by date descending
  return transactions.sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
}

// Rich mock offers data
const MOCK_OFFERS: Offer[] = [
  {
    id: 'offer-1',
    name: '20% Off Next Booking',
    description: 'Save 20% on your next hotel stay. Valid at all participating properties.',
    offer_type: 'percentage_discount',
    discount_value: 20,
    points_cost: 500,
    min_order_value: 100,
    valid_from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    valid_until: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(),
    is_active: true,
  },
  {
    id: 'offer-2',
    name: 'Free Room Upgrade',
    description: 'Upgrade to the next room category at no extra charge. Subject to availability.',
    offer_type: 'free_item',
    points_cost: 750,
    valid_from: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
    valid_until: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000).toISOString(),
    is_active: true,
  },
  {
    id: 'offer-3',
    name: '$25 Restaurant Credit',
    description: 'Get $25 credit to use at any of our partner restaurants.',
    offer_type: 'fixed_discount',
    discount_value: 25,
    points_cost: 400,
    valid_from: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    valid_until: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
    is_active: true,
  },
  {
    id: 'offer-4',
    name: 'Double Points Weekend',
    description: 'Earn 2x points on all bookings made this weekend. Book now!',
    offer_type: 'points_reward',
    points_cost: 0,
    valid_from: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    valid_until: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
    is_active: true,
  },
  {
    id: 'offer-5',
    name: 'Complimentary Breakfast',
    description: 'Enjoy a free breakfast for two during your next hotel stay.',
    offer_type: 'free_item',
    points_cost: 300,
    valid_from: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    valid_until: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
    is_active: true,
  },
  {
    id: 'offer-6',
    name: 'Spa Day Package',
    description: 'Redeem for a relaxing spa day including massage and facial treatment.',
    offer_type: 'free_item',
    points_cost: 1500,
    valid_from: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    valid_until: new Date(Date.now() + 120 * 24 * 60 * 60 * 1000).toISOString(),
    is_active: true,
  },
  {
    id: 'offer-7',
    name: '15% Off Dining',
    description: 'Save 15% on your next restaurant bill at any partner venue.',
    offer_type: 'percentage_discount',
    discount_value: 15,
    points_cost: 250,
    valid_from: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
    valid_until: new Date(Date.now() + 40 * 24 * 60 * 60 * 1000).toISOString(),
    is_active: true,
  },
  {
    id: 'offer-8',
    name: 'Late Checkout',
    description: 'Extend your checkout time until 2 PM. Perfect for lazy mornings.',
    offer_type: 'free_item',
    points_cost: 200,
    valid_from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    valid_until: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(),
    is_active: true,
  },
];

// Store redeemed offers per user
const redeemedOffers: Record<string, Set<string>> = {};

export class MockLoyaltyService {
  async getMemberStatus(guestId: string): Promise<LoyaltyMember> {
    await delay(300);
    return getOrCreateMember(guestId);
  }

  async getPointsHistory(guestId: string, limit = 20): Promise<PointsHistoryResponse> {
    await delay(400);
    const member = getOrCreateMember(guestId);
    const items = generatePointsHistory(guestId, limit);
    
    return {
      items,
      total: items.length,
      current_balance: member.points_balance,
    };
  }

  async getAvailableOffers(guestId?: string): Promise<Offer[]> {
    await delay(300);
    
    // Filter out already redeemed offers for this user
    const userRedeemed = guestId ? (redeemedOffers[guestId] || new Set()) : new Set();
    return MOCK_OFFERS.filter(offer => 
      offer.is_active && 
      !userRedeemed.has(offer.id) &&
      new Date(offer.valid_until) > new Date()
    );
  }

  async redeemOffer(guestId: string, offerId: string): Promise<{ success: boolean; message: string; remaining_points: number }> {
    await delay(500);
    
    const member = getOrCreateMember(guestId);
    const offer = MOCK_OFFERS.find(o => o.id === offerId);
    
    if (!offer) {
      throw new Error('Offer not found');
    }
    
    if (!redeemedOffers[guestId]) {
      redeemedOffers[guestId] = new Set();
    }
    
    if (redeemedOffers[guestId].has(offerId)) {
      throw new Error('Offer already redeemed');
    }
    
    if (offer.points_cost && member.points_balance < offer.points_cost) {
      throw new Error('Insufficient points');
    }
    
    // Deduct points
    if (offer.points_cost) {
      member.points_balance -= offer.points_cost;
      mockMemberData[guestId] = member;
    }
    
    // Mark as redeemed
    redeemedOffers[guestId].add(offerId);
    
    return {
      success: true,
      message: `Successfully redeemed "${offer.name}"!`,
      remaining_points: member.points_balance,
    };
  }

  async earnPoints(guestId: string, points: number, description: string): Promise<LoyaltyMember> {
    await delay(300);
    
    const member = getOrCreateMember(guestId);
    member.points_balance += points;
    member.lifetime_points += points;
    
    // Check for tier upgrade
    const tiers: LoyaltyTier[] = ['bronze', 'silver', 'gold', 'platinum'];
    const tierThresholds = [0, 1000, 5000, 15000];
    const currentTierIndex = tiers.indexOf(member.tier);
    
    for (let i = tiers.length - 1; i > currentTierIndex; i--) {
      if (member.lifetime_points >= tierThresholds[i]) {
        member.tier = tiers[i];
        member.next_tier = i < 3 ? tiers[i + 1] : undefined;
        member.points_to_next_tier = i < 3 ? tierThresholds[i + 1] - member.lifetime_points : undefined;
        break;
      }
    }
    
    mockMemberData[guestId] = member;
    return member;
  }
}
