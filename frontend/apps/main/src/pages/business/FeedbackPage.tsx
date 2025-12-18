import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MessageSquare, TrendingUp, ThumbsUp, ThumbsDown, Minus, Filter } from 'lucide-react';
import { apiServices, useAuthStore } from '@/stores/authStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

type SentimentFilter = 'all' | 'positive' | 'neutral' | 'negative';
type StatusFilter = 'all' | 'pending' | 'analyzed' | 'reviewed';

const sentimentConfig = {
  positive: { icon: ThumbsUp, color: 'text-green-600', bg: 'bg-green-100' },
  neutral: { icon: Minus, color: 'text-slate-600', bg: 'bg-slate-100' },
  negative: { icon: ThumbsDown, color: 'text-red-600', bg: 'bg-red-100' },
};

export default function FeedbackPage() {
  const { businessContext } = useAuthStore();
  const venueId = businessContext?.businessId;
  
  const [sentimentFilter, setSentimentFilter] = useState<SentimentFilter>('all');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [page, setPage] = useState(1);

  // Get insights summary
  const { data: insights, isLoading: insightsLoading } = useQuery({
    queryKey: ['venue-insights', venueId],
    queryFn: async () => {
      if (!venueId) return null;
      try {
        return await apiServices.feedback.getVenueInsights(venueId);
      } catch {
        return null;
      }
    },
    enabled: !!venueId,
  });

  // Get feedback list
  const { data: feedbackList, isLoading: feedbackLoading } = useQuery({
    queryKey: ['feedback-list', venueId, statusFilter, page],
    queryFn: async () => {
      return await apiServices.feedback.listFeedback({
        venue_id: venueId,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        page,
        page_size: 20,
      });
    },
  });

  // Filter by sentiment client-side
  const filteredFeedback = feedbackList?.items?.filter((item) => {
    if (sentimentFilter === 'all') return true;
    return item.sentiment?.sentiment === sentimentFilter;
  }) || [];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Customer Feedback</h1>
        <p className="text-slate-600">Monitor and analyze customer feedback and sentiment</p>
      </div>

      {/* Insights Summary */}
      {insights && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <MessageSquare className="w-8 h-8 text-blue-600" />
                <TrendingUp className="w-5 h-5 text-green-600" />
              </div>
              <p className="text-sm text-slate-600">Total Feedback</p>
              <p className="text-3xl font-bold text-slate-900">{insights.total_feedback}</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="flex">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <span key={star} className={star <= Math.round(insights.average_rating) ? 'text-yellow-400' : 'text-slate-300'}>★</span>
                  ))}
                </div>
              </div>
              <p className="text-sm text-slate-600">Average Rating</p>
              <p className="text-3xl font-bold text-slate-900">{insights.average_rating.toFixed(1)}</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <ThumbsUp className="w-5 h-5 text-green-600" />
                <span className="text-sm text-green-600 font-medium">Positive</span>
              </div>
              <p className="text-3xl font-bold text-slate-900">
                {Math.round(insights.sentiment_distribution.positive * 100)}%
              </p>
              <div className="w-full h-2 bg-slate-200 rounded-full mt-2">
                <div 
                  className="h-full bg-green-500 rounded-full"
                  style={{ width: `${insights.sentiment_distribution.positive * 100}%` }}
                />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <p className="text-sm text-slate-600 mb-2">vs Platform Average</p>
              <p className={`text-3xl font-bold ${insights.vs_platform_average >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {insights.vs_platform_average >= 0 ? '+' : ''}{(insights.vs_platform_average * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {insights.vs_platform_average >= 0 ? 'Above' : 'Below'} average
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Improvement Areas */}
      {insights?.areas_for_improvement && insights.areas_for_improvement.length > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Areas for Improvement</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {insights.areas_for_improvement.map((area, idx) => (
                <span key={idx} className="px-3 py-1 bg-amber-100 text-amber-800 rounded-full text-sm">
                  {area}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-500" />
              <span className="text-sm font-medium text-slate-700">Filters:</span>
            </div>
            
            <div className="flex gap-2">
              {(['all', 'positive', 'neutral', 'negative'] as SentimentFilter[]).map((sentiment) => (
                <button
                  key={sentiment}
                  onClick={() => setSentimentFilter(sentiment)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    sentimentFilter === sentiment
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  {sentiment === 'all' ? 'All Sentiment' : sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}
                </button>
              ))}
            </div>

            <div className="flex gap-2 ml-4">
              {(['all', 'pending', 'analyzed', 'reviewed'] as StatusFilter[]).map((status) => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    statusFilter === status
                      ? 'bg-purple-600 text-white'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  {status === 'all' ? 'All Status' : status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Feedback List */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Feedback</CardTitle>
        </CardHeader>
        <CardContent>
          {feedbackLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : filteredFeedback.length > 0 ? (
            <div className="space-y-4">
              {filteredFeedback.map((feedback) => {
                const sentiment = feedback.sentiment?.sentiment || 'neutral';
                const config = sentimentConfig[sentiment];
                const SentimentIcon = config.icon;
                
                return (
                  <div key={feedback.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${config.bg}`}>
                          <SentimentIcon className={`w-5 h-5 ${config.color}`} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-slate-900 capitalize">{feedback.category}</span>
                            <span className={`px-2 py-0.5 rounded-full text-xs ${config.bg} ${config.color}`}>
                              {sentiment}
                            </span>
                          </div>
                          <div className="flex items-center gap-1 mt-1">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <span key={star} className={`text-sm ${star <= feedback.rating ? 'text-yellow-400' : 'text-slate-300'}`}>★</span>
                            ))}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          feedback.status === 'analyzed' ? 'bg-green-100 text-green-700' :
                          feedback.status === 'reviewed' ? 'bg-blue-100 text-blue-700' :
                          'bg-slate-100 text-slate-700'
                        }`}>
                          {feedback.status}
                        </span>
                        <p className="text-xs text-slate-500 mt-1">
                          {new Date(feedback.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    {feedback.comment && (
                      <p className="text-slate-700 text-sm">{feedback.comment}</p>
                    )}
                    {feedback.sentiment?.key_phrases && feedback.sentiment.key_phrases.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-3">
                        {feedback.sentiment.key_phrases.map((phrase, idx) => (
                          <span key={idx} className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">
                            {phrase}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-12">
              <MessageSquare className="w-12 h-12 text-slate-200 mx-auto mb-3" />
              <p className="text-slate-500">No feedback found</p>
            </div>
          )}

          {/* Pagination */}
          {feedbackList && feedbackList.has_more && (
            <div className="flex justify-center gap-2 mt-6">
              <Button
                variant="outline"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              <span className="px-4 py-2 text-slate-600">Page {page}</span>
              <Button
                variant="outline"
                onClick={() => setPage(p => p + 1)}
                disabled={!feedbackList.has_more}
              >
                Next
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
