import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Megaphone, Plus, Play, Pause, Calendar, Target, DollarSign, Users } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import type { CampaignStatus, CampaignType } from '@hospitality-platform/api-client';

const statusColors: Record<string, string> = {
  draft: 'bg-slate-100 text-slate-700',
  scheduled: 'bg-blue-100 text-blue-700',
  active: 'bg-green-100 text-green-700',
  paused: 'bg-yellow-100 text-yellow-700',
  completed: 'bg-purple-100 text-purple-700',
  cancelled: 'bg-red-100 text-red-700',
};

const typeLabels: Record<string, string> = {
  discount: '% Discount',
  points_multiplier: 'Points Multiplier',
  bonus_points: 'Bonus Points',
  free_item: 'Free Item',
  bundle: 'Bundle Deal',
};

export default function CampaignsPage() {
  const queryClient = useQueryClient();
  const { businessContext } = useAuthStore();
  const venueId = businessContext?.businessId;
  
  const [statusFilter, setStatusFilter] = useState<CampaignStatus | 'all'>('all');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newCampaign, setNewCampaign] = useState({
    name: '',
    description: '',
    campaign_type: 'discount' as CampaignType,
    start_date: '',
    end_date: '',
    discount_percentage: 10,
  });

  // Get campaigns
  const { data: campaigns, isLoading } = useQuery({
    queryKey: ['campaigns', venueId, statusFilter],
    queryFn: async () => {
      return await apiServices.campaigns.listCampaigns({
        venue_id: venueId,
        status: statusFilter !== 'all' ? statusFilter as CampaignStatus : undefined,
        page: 1,
        page_size: 50,
      });
    },
  });

  // Get active campaigns count
  const { data: activeCampaigns } = useQuery({
    queryKey: ['active-campaigns', venueId],
    queryFn: () => apiServices.campaigns.getActiveCampaigns(venueId),
  });

  const createMutation = useMutation({
    mutationFn: () => apiServices.campaigns.createCampaign({
      ...newCampaign,
      venue_id: venueId,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      setShowCreateForm(false);
      setNewCampaign({
        name: '',
        description: '',
        campaign_type: 'discount',
        start_date: '',
        end_date: '',
        discount_percentage: 10,
      });
    },
  });

  const activateMutation = useMutation({
    mutationFn: (campaignId: string) => apiServices.campaigns.activateCampaign(campaignId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      queryClient.invalidateQueries({ queryKey: ['active-campaigns'] });
    },
  });

  const pauseMutation = useMutation({
    mutationFn: (campaignId: string) => apiServices.campaigns.pauseCampaign(campaignId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      queryClient.invalidateQueries({ queryKey: ['active-campaigns'] });
    },
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Marketing Campaigns</h1>
          <p className="text-slate-600">Create and manage promotional campaigns</p>
        </div>
        <Button onClick={() => setShowCreateForm(true)} leftIcon={<Plus className="w-5 h-5" />}>
          New Campaign
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <Megaphone className="w-8 h-8 text-blue-600" />
            </div>
            <p className="text-sm text-slate-600">Total Campaigns</p>
            <p className="text-3xl font-bold text-slate-900">{campaigns?.total || 0}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <Play className="w-8 h-8 text-green-600" />
            </div>
            <p className="text-sm text-slate-600">Active Now</p>
            <p className="text-3xl font-bold text-green-600">{activeCampaigns?.length || 0}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <Target className="w-8 h-8 text-purple-600" />
            </div>
            <p className="text-sm text-slate-600">Draft</p>
            <p className="text-3xl font-bold text-slate-900">
              {campaigns?.items?.filter(c => c.status === 'draft').length || 0}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Create Campaign Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-lg">
            <CardHeader>
              <CardTitle>Create New Campaign</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Campaign Name</label>
                  <Input
                    value={newCampaign.name}
                    onChange={(e) => setNewCampaign({ ...newCampaign, name: e.target.value })}
                    placeholder="e.g., Summer Sale"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
                  <textarea
                    value={newCampaign.description}
                    onChange={(e) => setNewCampaign({ ...newCampaign, description: e.target.value })}
                    placeholder="Describe your campaign..."
                    rows={3}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Campaign Type</label>
                  <select
                    value={newCampaign.campaign_type}
                    onChange={(e) => setNewCampaign({ ...newCampaign, campaign_type: e.target.value as CampaignType })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="discount">Percentage Discount</option>
                    <option value="points_multiplier">Points Multiplier</option>
                    <option value="bonus_points">Bonus Points</option>
                    <option value="free_item">Free Item</option>
                    <option value="bundle">Bundle Deal</option>
                  </select>
                </div>

                {newCampaign.campaign_type === 'discount' && (
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Discount %</label>
                    <Input
                      type="number"
                      min={1}
                      max={100}
                      value={newCampaign.discount_percentage}
                      onChange={(e) => setNewCampaign({ ...newCampaign, discount_percentage: parseInt(e.target.value) || 0 })}
                    />
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Start Date</label>
                    <Input
                      type="date"
                      value={newCampaign.start_date}
                      onChange={(e) => setNewCampaign({ ...newCampaign, start_date: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">End Date</label>
                    <Input
                      type="date"
                      value={newCampaign.end_date}
                      onChange={(e) => setNewCampaign({ ...newCampaign, end_date: e.target.value })}
                    />
                  </div>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setShowCreateForm(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => createMutation.mutate()}
                    disabled={!newCampaign.name || !newCampaign.start_date || !newCampaign.end_date || createMutation.isPending}
                    className="flex-1"
                  >
                    {createMutation.isPending ? 'Creating...' : 'Create Campaign'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filter */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-slate-700">Status:</span>
            <div className="flex gap-2">
              {(['all', 'draft', 'active', 'paused', 'completed'] as const).map((status) => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    statusFilter === status
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  {status === 'all' ? 'All' : status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Campaigns List */}
      <Card>
        <CardHeader>
          <CardTitle>Campaigns</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : campaigns?.items && campaigns.items.length > 0 ? (
            <div className="space-y-4">
              {campaigns.items.map((campaign) => (
                <div key={campaign.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold text-slate-900">{campaign.name}</h4>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColors[campaign.status]}`}>
                          {campaign.status}
                        </span>
                      </div>
                      <p className="text-sm text-slate-600 mb-2">{campaign.description}</p>
                      <div className="flex items-center gap-4 text-sm text-slate-500">
                        <span className="flex items-center gap-1">
                          <Target className="w-4 h-4" />
                          {typeLabels[campaign.campaign_type]}
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {new Date(campaign.start_date).toLocaleDateString()} - {new Date(campaign.end_date).toLocaleDateString()}
                        </span>
                        {campaign.discount_percentage && (
                          <span className="flex items-center gap-1">
                            <DollarSign className="w-4 h-4" />
                            {campaign.discount_percentage}% off
                          </span>
                        )}
                        {campaign.current_uses !== undefined && campaign.max_uses && (
                          <span className="flex items-center gap-1">
                            <Users className="w-4 h-4" />
                            {campaign.current_uses}/{campaign.max_uses} used
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {campaign.status === 'draft' && (
                        <Button
                          size="sm"
                          onClick={() => activateMutation.mutate(campaign.id)}
                          disabled={activateMutation.isPending}
                          leftIcon={<Play className="w-4 h-4" />}
                        >
                          Activate
                        </Button>
                      )}
                      {campaign.status === 'active' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => pauseMutation.mutate(campaign.id)}
                          disabled={pauseMutation.isPending}
                          leftIcon={<Pause className="w-4 h-4" />}
                        >
                          Pause
                        </Button>
                      )}
                      {campaign.status === 'paused' && (
                        <Button
                          size="sm"
                          onClick={() => activateMutation.mutate(campaign.id)}
                          disabled={activateMutation.isPending}
                          leftIcon={<Play className="w-4 h-4" />}
                        >
                          Resume
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Megaphone className="w-12 h-12 text-slate-200 mx-auto mb-3" />
              <p className="text-slate-500">No campaigns found</p>
              <Button className="mt-4" onClick={() => setShowCreateForm(true)}>
                Create Your First Campaign
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
