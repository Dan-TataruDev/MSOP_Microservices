import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Settings, Heart, History, Eye, Plus, X, Save, TrendingUp, Filter } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { formatDate } from '@hospitality-platform/utils';

type TabType = 'preferences' | 'interactions' | 'personalization';

export default function PreferencesPage() {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>('preferences');
  const [showAddPreference, setShowAddPreference] = useState(false);
  const [newPreference, setNewPreference] = useState({ key: '', value: '', category: '' });

  // Get guest profile
  const { data: guestProfile } = useQuery({
    queryKey: ['guest-profile', user?.id],
    queryFn: async () => {
      if (!user?.id) return null;
      try {
        const response = await apiServices.personalization.getCurrentGuestProfile();
        return response.data;
      } catch {
        return null;
      }
    },
    enabled: !!user?.id,
  });

  // Get preferences
  const { data: preferences, isLoading: preferencesLoading } = useQuery({
    queryKey: ['guest-preferences', user?.id],
    queryFn: async () => {
      if (!user?.id) return [];
      try {
        const response = await apiServices.personalization.getGuestPreferences(user.id);
        return response.data || [];
      } catch {
        return [];
      }
    },
    enabled: !!user?.id && activeTab === 'preferences',
  });

  // Get preference categories
  const { data: categories } = useQuery({
    queryKey: ['preference-categories'],
    queryFn: async () => {
      try {
        const response = await apiServices.personalization.getPreferenceCategories();
        return response.data || [];
      } catch {
        return [];
      }
    },
  });

  // Get interactions
  const { data: interactions, isLoading: interactionsLoading } = useQuery({
    queryKey: ['guest-interactions', user?.id],
    queryFn: async () => {
      if (!user?.id) return [];
      try {
        const response = await apiServices.personalization.getGuestInteractions(user.id, {
          limit: 50,
        });
        return response.data || [];
      } catch {
        return [];
      }
    },
    enabled: !!user?.id && activeTab === 'interactions',
  });

  // Get personalization context
  const { data: personalizationContext, isLoading: contextLoading } = useQuery({
    queryKey: ['personalization-context', user?.id],
    queryFn: async () => {
      if (!user?.id) return null;
      try {
        const response = await apiServices.personalization.getPersonalizationContext(user.id);
        return response.data;
      } catch {
        return null;
      }
    },
    enabled: !!user?.id && activeTab === 'personalization',
  });

  // Get segments
  const { data: segments } = useQuery({
    queryKey: ['guest-segments', user?.id],
    queryFn: async () => {
      if (!user?.id) return [];
      try {
        const response = await apiServices.personalization.getGuestSegments(user.id);
        return response.data || [];
      } catch {
        return [];
      }
    },
    enabled: !!user?.id && activeTab === 'personalization',
  });

  // Get behavior signals
  const { data: behaviorSignals } = useQuery({
    queryKey: ['behavior-signals', user?.id],
    queryFn: async () => {
      if (!user?.id) return [];
      try {
        const response = await apiServices.personalization.getBehaviorSignals(user.id);
        return response.data || [];
      } catch {
        return [];
      }
    },
    enabled: !!user?.id && activeTab === 'personalization',
  });

  const createPreferenceMutation = useMutation({
    mutationFn: () => apiServices.personalization.createPreference(user!.id, {
      key: newPreference.key,
      value: newPreference.value,
      category: newPreference.category || undefined,
      source: 'explicit',
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guest-preferences'] });
      setShowAddPreference(false);
      setNewPreference({ key: '', value: '', category: '' });
    },
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Preferences & Personalization</h1>
        <p className="text-slate-600">Manage your preferences, view interaction history, and see how we personalize your experience</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-slate-200">
        {(['preferences', 'interactions', 'personalization'] as TabType[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 font-medium transition-colors border-b-2 capitalize ${
              activeTab === tab
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Preferences Tab */}
      {activeTab === 'preferences' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <Heart className="w-5 h-5 mr-2" />
                  My Preferences
                </CardTitle>
                <Button size="sm" onClick={() => setShowAddPreference(true)} leftIcon={<Plus className="w-4 h-4" />}>
                  Add Preference
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {preferencesLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                </div>
              ) : preferences && preferences.length > 0 ? (
                <div className="space-y-3">
                  {preferences.map((pref: any) => (
                    <div key={pref.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className="font-semibold text-slate-900 capitalize">
                              {pref.key.replace(/_/g, ' ')}
                            </h4>
                            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs capitalize">
                              {pref.source}
                            </span>
                            {pref.category && (
                              <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs">
                                {pref.category}
                              </span>
                            )}
                          </div>
                          <div className="mt-2">
                            {Array.isArray(pref.value) ? (
                              <div className="flex flex-wrap gap-2">
                                {pref.value.map((item: string, idx: number) => (
                                  <span
                                    key={idx}
                                    className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                                  >
                                    {item}
                                  </span>
                                ))}
                              </div>
                            ) : (
                              <p className="text-slate-700">{String(pref.value)}</p>
                            )}
                          </div>
                          {pref.updated_at && (
                            <p className="text-xs text-slate-500 mt-2">
                              Updated {formatDate(pref.updated_at)}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Heart className="w-12 h-12 text-slate-200 mx-auto mb-3" />
                  <p className="text-slate-500 mb-4">No preferences set yet</p>
                  <Button onClick={() => setShowAddPreference(true)}>Add Your First Preference</Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Add Preference Modal */}
          {showAddPreference && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
              <Card className="w-full max-w-lg">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Add Preference</CardTitle>
                    <button onClick={() => setShowAddPreference(false)}>
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Preference Key</label>
                      <Input
                        value={newPreference.key}
                        onChange={(e) => setNewPreference({ ...newPreference, key: e.target.value })}
                        placeholder="e.g., dietary_restrictions"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Value</label>
                      <Input
                        value={newPreference.value}
                        onChange={(e) => setNewPreference({ ...newPreference, value: e.target.value })}
                        placeholder="e.g., vegetarian, gluten-free"
                      />
                    </div>
                    {categories && categories.length > 0 && (
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Category</label>
                        <select
                          value={newPreference.category}
                          onChange={(e) => setNewPreference({ ...newPreference, category: e.target.value })}
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                        >
                          <option value="">Select category</option>
                          {categories.map((cat: any) => (
                            <option key={cat.id} value={cat.key}>{cat.name}</option>
                          ))}
                        </select>
                      </div>
                    )}
                    <div className="flex gap-3 pt-4">
                      <Button
                        variant="outline"
                        onClick={() => setShowAddPreference(false)}
                        className="flex-1"
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={() => createPreferenceMutation.mutate()}
                        disabled={!newPreference.key || !newPreference.value || createPreferenceMutation.isPending}
                        className="flex-1"
                        leftIcon={<Save className="w-4 h-4" />}
                      >
                        Save
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      )}

      {/* Interactions Tab */}
      {activeTab === 'interactions' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <History className="w-5 h-5 mr-2" />
              Interaction History
            </CardTitle>
          </CardHeader>
          <CardContent>
            {interactionsLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              </div>
            ) : interactions && interactions.length > 0 ? (
              <div className="space-y-3">
                {interactions.map((interaction: any) => (
                  <div key={interaction.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-semibold text-slate-900 capitalize">
                            {interaction.interaction_type?.replace(/_/g, ' ') || 'Interaction'}
                          </h4>
                          {interaction.entity_type && (
                            <span className="px-2 py-0.5 bg-slate-100 text-slate-700 rounded text-xs capitalize">
                              {interaction.entity_type}
                            </span>
                          )}
                        </div>
                        {interaction.metadata && (
                          <div className="text-sm text-slate-600 space-y-1">
                            {Object.entries(interaction.metadata).map(([key, value]: [string, any]) => (
                              <div key={key}>
                                <span className="font-medium">{key}:</span> {String(value)}
                              </div>
                            ))}
                          </div>
                        )}
                        <p className="text-xs text-slate-500 mt-2">
                          {formatDate(interaction.timestamp || interaction.created_at)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <History className="w-12 h-12 text-slate-200 mx-auto mb-3" />
                <p className="text-slate-500">No interactions recorded yet</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Personalization Tab */}
      {activeTab === 'personalization' && (
        <div className="space-y-6">
          {contextLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : (
            <>
              {/* Segments */}
              {segments && segments.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <TrendingUp className="w-5 h-5 mr-2" />
                      Your Segments
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {segments.map((segment: any) => (
                        <span
                          key={segment.id}
                          className="px-3 py-1 bg-gradient-to-r from-purple-100 to-blue-100 text-purple-800 rounded-full text-sm font-medium"
                        >
                          {segment.segment_name || segment.name}
                        </span>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Behavior Signals */}
              {behaviorSignals && behaviorSignals.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Eye className="w-5 h-5 mr-2" />
                      Behavior Signals
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {behaviorSignals.map((signal: any) => (
                        <div key={signal.id} className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-slate-900 capitalize">
                              {signal.signal_type?.replace(/_/g, ' ') || 'Signal'}
                            </span>
                            {signal.confidence && (
                              <span className="text-xs text-slate-600">
                                Confidence: {Math.round(signal.confidence * 100)}%
                              </span>
                            )}
                          </div>
                          {signal.description && (
                            <p className="text-sm text-slate-600 mt-1">{signal.description}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Personalization Context Summary */}
              {personalizationContext && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Settings className="w-5 h-5 mr-2" />
                      Personalization Summary
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-sm text-slate-600">Total Preferences</p>
                        <p className="text-2xl font-bold text-slate-900">
                          {personalizationContext.preference_count || preferences?.length || 0}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-slate-600">Total Interactions</p>
                        <p className="text-2xl font-bold text-slate-900">
                          {personalizationContext.interaction_count || interactions?.length || 0}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-slate-600">Active Segments</p>
                        <p className="text-2xl font-bold text-slate-900">
                          {segments?.length || 0}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
