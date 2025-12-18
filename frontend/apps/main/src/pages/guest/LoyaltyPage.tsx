import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Trophy, Star, Gift, Clock, Check, Loader2 } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import type { LoyaltyTier, Offer } from '@hospitality-platform/api-client';

const tierConfig: Record<LoyaltyTier, { color: string; bgColor: string; icon: string }> = {
  bronze: { color: 'text-amber-700', bgColor: 'bg-amber-100', icon: '🥉' },
  silver: { color: 'text-slate-500', bgColor: 'bg-slate-100', icon: '🥈' },
  gold: { color: 'text-yellow-600', bgColor: 'bg-yellow-100', icon: '🥇' },
  platinum: { color: 'text-purple-600', bgColor: 'bg-purple-100', icon: '💎' },
};

export default function LoyaltyPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { isAuthenticated, user } = useAuthStore();
  const [redeemingId, setRedeemingId] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const { data: member, isLoading: memberLoading } = useQuery({
    queryKey: ['loyalty-member', user?.id],
    queryFn: async () => {
      if (!user?.id) throw new Error('User ID required');
      return await apiServices.loyalty.getMemberStatus(user.id);
    },
    enabled: isAuthenticated && !!user?.id,
  });

  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ['points-history', user?.id],
    queryFn: async () => {
      if (!user?.id) throw new Error('User ID required');
      return await apiServices.loyalty.getPointsHistory(user.id, 10);
    },
    enabled: isAuthenticated && !!user?.id,
  });

  const { data: offers } = useQuery({
    queryKey: ['available-offers', user?.id],
    queryFn: async () => {
      return await apiServices.loyalty.getAvailableOffers(user?.id);
    },
    enabled: isAuthenticated,
  });

  const redeemMutation = useMutation({
    mutationFn: async (offerId: string) => {
      if (!user?.id) throw new Error('User ID required');
      return await apiServices.loyalty.redeemOffer(user.id, offerId);
    },
    onMutate: (offerId) => setRedeemingId(offerId),
    onSuccess: (result) => {
      setSuccessMessage(result.message);
      queryClient.invalidateQueries({ queryKey: ['loyalty-member', user?.id] });
      queryClient.invalidateQueries({ queryKey: ['available-offers', user?.id] });
      queryClient.invalidateQueries({ queryKey: ['points-history', user?.id] });
      setTimeout(() => setSuccessMessage(null), 3000);
    },
    onSettled: () => setRedeemingId(null),
  });

  const canRedeem = (offer: Offer) => {
    if (!offer.points_cost || offer.points_cost === 0) return true;
    return (member?.points_balance || 0) >= offer.points_cost;
  };

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <Trophy className="w-16 h-16 text-slate-300 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-slate-900 mb-2">Join Our Loyalty Program</h1>
        <p className="text-slate-600 mb-6">Earn points, unlock rewards, and enjoy exclusive benefits</p>
        <Button onClick={() => navigate('/login')}>Sign In to Join</Button>
      </div>
    );
  }

  if (memberLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  const tier = member?.tier || 'bronze';
  const config = tierConfig[tier];
  const progressPercent = member?.points_to_next_tier && member?.lifetime_points
    ? Math.min(100, ((member.lifetime_points) / (member.lifetime_points + member.points_to_next_tier)) * 100)
    : 100;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Loyalty Program</h1>
        <p className="text-slate-600">Earn points with every booking and unlock exclusive rewards</p>
      </div>

      {/* Status Card */}
      <Card className="mb-8 overflow-hidden">
        <div className={`${config.bgColor} p-8`}>
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className="text-4xl">{config.icon}</span>
                <div>
                  <h2 className={`text-3xl font-bold capitalize ${config.color}`}>{tier} Member</h2>
                  <p className="text-slate-600">Member since {member?.joined_at ? new Date(member.joined_at).toLocaleDateString() : 'N/A'}</p>
                </div>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-slate-600 mb-1">Points Balance</p>
              <p className="text-4xl font-bold text-slate-900">{member?.points_balance?.toLocaleString() || 0}</p>
            </div>
          </div>
        </div>
        
        {member?.next_tier && member?.points_to_next_tier && (
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-600">Progress to {member.next_tier}</span>
              <span className="text-sm font-semibold text-slate-900">
                {member.points_to_next_tier.toLocaleString()} points to go
              </span>
            </div>
            <div className="w-full h-3 bg-slate-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-500"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </CardContent>
        )}
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Points History */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Clock className="w-5 h-5 mr-2" />
              Points History
            </CardTitle>
          </CardHeader>
          <CardContent>
            {historyLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              </div>
            ) : history?.items && history.items.length > 0 ? (
              <div className="space-y-4">
                {history.items.map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between py-3 border-b border-slate-100 last:border-b-0">
                    <div>
                      <p className="font-medium text-slate-900">{transaction.description}</p>
                      <p className="text-xs text-slate-500">
                        {new Date(transaction.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <span className={`font-bold ${transaction.points >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {transaction.points >= 0 ? '+' : ''}{transaction.points}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-slate-500 py-8">No transactions yet</p>
            )}
          </CardContent>
        </Card>

        {/* Available Offers */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Gift className="w-5 h-5 mr-2" />
              Available Rewards
            </CardTitle>
          </CardHeader>
          <CardContent>
            {successMessage && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
                <Check className="w-5 h-5 text-green-600" />
                <span className="text-green-800 text-sm font-medium">{successMessage}</span>
              </div>
            )}
            {offers && offers.length > 0 ? (
              <div className="space-y-4">
                {offers.map((offer) => {
                  const isRedeeming = redeemingId === offer.id;
                  const affordable = canRedeem(offer);
                  const isFree = !offer.points_cost || offer.points_cost === 0;
                  
                  return (
                    <div key={offer.id} className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <h4 className="font-semibold text-slate-900">{offer.name}</h4>
                            {isFree && (
                              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">FREE</span>
                            )}
                          </div>
                          <p className="text-sm text-slate-600 mt-1">{offer.description}</p>
                          <div className="flex items-center gap-3 mt-2">
                            {offer.points_cost && offer.points_cost > 0 && (
                              <span className={`text-xs font-medium ${affordable ? 'text-blue-600' : 'text-red-500'}`}>
                                {offer.points_cost.toLocaleString()} points
                              </span>
                            )}
                            <span className="text-xs text-slate-400">
                              Expires {new Date(offer.valid_until).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          disabled={!affordable || isRedeeming}
                          onClick={() => redeemMutation.mutate(offer.id)}
                          className="flex-shrink-0"
                        >
                          {isRedeeming ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : isFree ? (
                            'Claim'
                          ) : affordable ? (
                            'Redeem'
                          ) : (
                            'Not enough'
                          )}
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8">
                <Gift className="w-12 h-12 text-slate-200 mx-auto mb-3" />
                <p className="text-slate-500">No rewards available right now</p>
                <p className="text-sm text-slate-400 mt-1">Check back soon for exclusive deals!</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Tier Benefits */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Star className="w-5 h-5 mr-2" />
            Tier Benefits
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {(['bronze', 'silver', 'gold', 'platinum'] as LoyaltyTier[]).map((t) => {
              const c = tierConfig[t];
              const isCurrentTier = t === tier;
              return (
                <div
                  key={t}
                  className={`p-4 rounded-xl border-2 ${
                    isCurrentTier ? 'border-blue-500 bg-blue-50' : 'border-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-2xl">{c.icon}</span>
                    <h4 className={`font-bold capitalize ${c.color}`}>{t}</h4>
                    {isCurrentTier && (
                      <span className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded-full">Current</span>
                    )}
                  </div>
                  <ul className="text-sm text-slate-600 space-y-1">
                    <li>• {t === 'bronze' ? '1x' : t === 'silver' ? '1.5x' : t === 'gold' ? '2x' : '3x'} points on bookings</li>
                    <li>• {t === 'platinum' ? 'Priority' : t === 'gold' ? 'Express' : 'Standard'} support</li>
                    {(t === 'gold' || t === 'platinum') && <li>• Exclusive offers</li>}
                    {t === 'platinum' && <li>• Free upgrades</li>}
                  </ul>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
