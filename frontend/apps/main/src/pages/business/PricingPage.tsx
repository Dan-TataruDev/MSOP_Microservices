import { useState } from 'react';

import { useQuery } from '@tanstack/react-query';

import { DollarSign, TrendingUp, Clock, Zap, Calculator } from 'lucide-react';

import { apiServices, useAuthStore } from '@/stores/authStore';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

import { Button } from '@/components/ui/Button';

import { Input } from '@/components/ui/Input';

import { formatCurrency } from '@hospitality-platform/utils';



const demandColors = {

  very_low: 'bg-blue-100 text-blue-700',

  low: 'bg-green-100 text-green-700',

  normal: 'bg-slate-100 text-slate-700',

  high: 'bg-orange-100 text-orange-700',

  very_high: 'bg-red-100 text-red-700',

};



export default function PricingPage() {

  const { businessContext } = useAuthStore();

  const venueId = businessContext?.businessId || 'demo';

  

  const [estimateDate, setEstimateDate] = useState('');

  const [estimateTime, setEstimateTime] = useState('');

  const [partySize, setPartySize] = useState(2);



  // Get pricing rules

  const { data: rules, isLoading: rulesLoading } = useQuery({

    queryKey: ['pricing-rules', venueId],

    queryFn: async () => {

      return await apiServices.pricing.listRules(venueId);

    },

    enabled: !!venueId,

  });



  // Get base prices

  const { data: basePrices, isLoading: pricesLoading } = useQuery({

    queryKey: ['base-prices', venueId],

    queryFn: async () => {

      if (!venueId) return [];

      return await apiServices.pricing.listBasePrices(venueId);

    },

    enabled: !!venueId,

  });



  // Price estimate query (triggered manually)

  const { data: estimate, refetch: fetchEstimate, isFetching: estimateLoading } = useQuery({

    queryKey: ['price-estimate', venueId, estimateDate, estimateTime, partySize],

    queryFn: async () => {

      if (!venueId || !estimateDate || !estimateTime) return null;

      const bookingTime = `${estimateDate}T${estimateTime}:00`;

      return await apiServices.pricing.getPriceEstimate({

        venue_id: venueId,

        venue_type: 'restaurant',

        booking_time: bookingTime,

        party_size: partySize,

        duration_minutes: 90,

      });

    },

    enabled: false,

  });



  const handleEstimate = () => {

    if (estimateDate && estimateTime) {

      fetchEstimate();

    }

  };



  return (

    <div className="container mx-auto px-4 py-8">

      <div className="mb-8">

        <h1 className="text-4xl font-bold text-slate-900 mb-2">Pricing Management</h1>

        <p className="text-slate-600">Configure dynamic pricing rules and preview price estimates</p>

      </div>



      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

        {/* Price Estimator */}

        <Card>

          <CardHeader>

            <CardTitle className="flex items-center">

              <Calculator className="w-5 h-5 mr-2" />

              Price Estimator

            </CardTitle>

          </CardHeader>

          <CardContent>

            <div className="space-y-4">

              <div className="grid grid-cols-2 gap-4">

                <div>

                  <label className="block text-sm font-medium text-slate-700 mb-1">Date</label>

                  <Input

                    type="date"

                    value={estimateDate}

                    onChange={(e) => setEstimateDate(e.target.value)}

                  />

                </div>

                <div>

                  <label className="block text-sm font-medium text-slate-700 mb-1">Time</label>

                  <Input

                    type="time"

                    value={estimateTime}

                    onChange={(e) => setEstimateTime(e.target.value)}

                  />

                </div>

              </div>

              <div>

                <label className="block text-sm font-medium text-slate-700 mb-1">Party Size</label>

                <Input

                  type="number"

                  min={1}

                  max={20}

                  value={partySize}

                  onChange={(e) => setPartySize(parseInt(e.target.value) || 1)}

                />

              </div>

              <Button

                onClick={handleEstimate}

                disabled={!estimateDate || !estimateTime || estimateLoading}

                className="w-full"

              >

                {estimateLoading ? 'Calculating...' : 'Get Price Estimate'}

              </Button>



              {estimate && (

                <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">

                  <div className="flex items-center justify-between mb-4">

                    <span className="text-sm text-slate-600">Estimated Price</span>

                    <span className={`px-2 py-1 rounded text-xs font-medium ${demandColors[estimate.demand_level]}`}>

                      {estimate.demand_level.replace('_', ' ')} demand

                    </span>

                  </div>

                  <p className="text-4xl font-bold text-slate-900 mb-2">

                    {formatCurrency(estimate.estimated_price, estimate.currency)}

                  </p>

                  {estimate.is_peak_time && (

                    <div className="flex items-center gap-1 text-orange-600 text-sm mb-2">

                      <Zap className="w-4 h-4" />

                      Peak time pricing applied

                    </div>

                  )}

                  {estimate.price_factors && estimate.price_factors.length > 0 && (

                    <div className="mt-3">

                      <p className="text-xs text-slate-500 mb-1">Price factors:</p>

                      <div className="flex flex-wrap gap-1">

                        {estimate.price_factors.map((factor, idx) => (

                          <span key={idx} className="px-2 py-0.5 bg-white rounded text-xs text-slate-600">

                            {factor}

                          </span>

                        ))}

                      </div>

                    </div>

                  )}

                </div>

              )}

            </div>

          </CardContent>

        </Card>



        {/* Active Rules */}

        <Card>

          <CardHeader>

            <CardTitle className="flex items-center">

              <Zap className="w-5 h-5 mr-2" />

              Active Pricing Rules

            </CardTitle>

          </CardHeader>

          <CardContent>

            {rulesLoading ? (

              <div className="text-center py-8">

                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>

              </div>

            ) : rules && rules.length > 0 ? (

              <div className="space-y-3">

                {rules.filter(r => r.is_active).map((rule) => (

                  <div key={rule.id} className="p-4 bg-slate-50 rounded-lg border border-slate-200">

                    <div className="flex items-center justify-between mb-2">

                      <h4 className="font-semibold text-slate-900">{rule.name}</h4>

                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${

                        rule.rule_type === 'demand_based' ? 'bg-purple-100 text-purple-700' :

                        rule.rule_type === 'time_based' ? 'bg-blue-100 text-blue-700' :

                        rule.rule_type === 'event_based' ? 'bg-orange-100 text-orange-700' :

                        'bg-green-100 text-green-700'

                      }`}>

                        {rule.rule_type.replace('_', ' ')}

                      </span>

                    </div>

                    <div className="flex items-center gap-4 text-sm text-slate-600">

                      <span>Priority: {rule.priority}</span>

                      <span>Multiplier: {rule.multiplier_min}x - {rule.multiplier_max}x</span>

                    </div>

                  </div>

                ))}

              </div>

            ) : (

              <div className="text-center py-8">

                <Zap className="w-12 h-12 text-slate-200 mx-auto mb-3" />

                <p className="text-slate-500">No pricing rules configured</p>

              </div>

            )}

          </CardContent>

        </Card>

      </div>



      {/* Base Prices */}

      <Card className="mt-8">

        <CardHeader>

          <CardTitle className="flex items-center">

            <DollarSign className="w-5 h-5 mr-2" />

            Base Prices

          </CardTitle>

        </CardHeader>

        <CardContent>

          {pricesLoading ? (

            <div className="text-center py-8">

              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>

            </div>

          ) : basePrices && basePrices.length > 0 ? (

            <div className="overflow-x-auto">

              <table className="w-full">

                <thead>

                  <tr className="border-b border-slate-200">

                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Category</th>

                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Base Price</th>

                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Effective From</th>

                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Effective To</th>

                  </tr>

                </thead>

                <tbody>

                  {basePrices.map((price) => (

                    <tr key={price.id} className="border-b border-slate-100">

                      <td className="py-3 px-4 text-slate-900">{price.item_category || 'Default'}</td>

                      <td className="py-3 px-4 font-semibold text-slate-900">

                        {formatCurrency(price.base_price, price.currency)}

                      </td>

                      <td className="py-3 px-4 text-slate-600 text-sm">

                        {new Date(price.effective_from).toLocaleDateString()}

                      </td>

                      <td className="py-3 px-4 text-slate-600 text-sm">

                        {price.effective_to ? new Date(price.effective_to).toLocaleDateString() : 'Ongoing'}

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          ) : (

            <div className="text-center py-8">

              <DollarSign className="w-12 h-12 text-slate-200 mx-auto mb-3" />

              <p className="text-slate-500">No base prices configured</p>

            </div>

          )}

        </CardContent>

      </Card>

    </div>

  );

}

