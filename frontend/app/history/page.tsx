'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/Spinner';
import { MetaScoreGauge } from '@/components/stats';
import { getStatsOverview } from '@/lib/api';
import { StatsOverviewResponse, MetricName } from '@/types';
import { METRIC_COLORS_LIGHT, META_SCORE_COLORS } from '@/lib/constants';
import {
  ArrowRight,
  Calendar,
  Filter,
  Search,
  PenSquare,
  TrendingUp,
  FileText,
} from 'lucide-react';

// Note: In a real app, we'd have an API endpoint to fetch evaluation history
// For MVP, we'll show a placeholder with stats overview

export default function HistoryPage() {
  const [stats, setStats] = useState<StatsOverviewResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getStatsOverview();
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load history');
      } finally {
        setIsLoading(false);
      }
    }
    fetchData();
  }, []);

  if (isLoading) {
    return <LoadingState message="Loading evaluation history..." />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-rose-500 mb-4">{error}</p>
        <Button onClick={() => window.location.reload()}>Retry</Button>
      </div>
    );
  }

  const hasEvaluations = stats && stats.total_evaluations > 0;

  // Generate mock history data based on stats (in a real app, this would come from API)
  const mockHistory = hasEvaluations
    ? Object.entries(stats.metrics_performance).map(([metric, perf], index) => ({
        id: `eval_mock_${index}`,
        metric: metric as MetricName,
        count: perf?.count || 0,
        avgGap: perf?.avg_gap || 0,
        trend: perf?.trend || 'insufficient_data',
      }))
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-500">
            {hasEvaluations
              ? `${stats.total_evaluations} evaluations completed`
              : 'No evaluations yet'}
          </p>
        </div>
        <Link href="/evaluate">
          <Button icon={<PenSquare className="w-4 h-4" />}>New Evaluation</Button>
        </Link>
      </div>

      {/* Filters */}
      <Card padding="sm">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-600">Filter:</span>
          </div>
          <div className="flex gap-2">
            {['all', 'Truthfulness', 'Safety', 'Clarity'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                  filter === f
                    ? 'bg-indigo-100 text-indigo-700 font-medium'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                {f === 'all' ? 'All Metrics' : f}
              </button>
            ))}
          </div>
          <div className="ml-auto relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search..."
              className="pl-10 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg w-48"
            />
          </div>
        </div>
      </Card>

      {/* Content */}
      {hasEvaluations ? (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <div className="flex items-center gap-4">
                <div className="p-3 bg-indigo-100 rounded-xl">
                  <FileText className="w-6 h-6 text-indigo-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-500">Total Evaluations</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {stats.total_evaluations}
                  </p>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-center gap-4">
                <MetaScoreGauge score={stats.average_meta_score} size="sm" showLabel={false} />
                <div>
                  <p className="text-sm text-slate-500">Average Score</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {stats.average_meta_score.toFixed(1)}/5
                  </p>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-center gap-4">
                <div className="p-3 bg-emerald-100 rounded-xl">
                  <TrendingUp className="w-6 h-6 text-emerald-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-500">Improvement</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {stats.improvement_trend}
                  </p>
                </div>
              </div>
            </Card>
          </div>

          {/* Metric Performance List */}
          <Card>
            <CardHeader
              title="Performance by Metric"
              subtitle="Your evaluation accuracy for each metric"
            />
            <div className="space-y-3">
              {mockHistory.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-4 bg-slate-50 rounded-xl hover:bg-slate-100 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <Badge className={METRIC_COLORS_LIGHT[item.metric]}>
                      {item.metric}
                    </Badge>
                    <div>
                      <p className="font-medium text-slate-900">
                        {item.count} evaluations
                      </p>
                      <p className="text-sm text-slate-500">
                        Avg gap: {item.avgGap.toFixed(2)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <Badge
                      variant={
                        item.trend === 'improving'
                          ? 'success'
                          : item.trend === 'declining'
                          ? 'error'
                          : 'default'
                      }
                    >
                      {item.trend.replace('_', ' ')}
                    </Badge>
                    <Link href={`/evaluate?metric=${item.metric}`}>
                      <Button variant="ghost" size="sm">
                        Practice
                        <ArrowRight className="w-4 h-4 ml-1" />
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Info Note */}
          <div className="text-center text-sm text-slate-400 py-4">
            <p>
              Note: Detailed evaluation history with individual feedback links will be available in a future update.
            </p>
          </div>
        </div>
      ) : (
        /* Empty State */
        <Card>
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">
              No Evaluations Yet
            </h3>
            <p className="text-slate-500 mb-6 max-w-md mx-auto">
              Start your first evaluation to begin tracking your AI assessment skills
              and receive expert feedback from GPT-4o.
            </p>
            <Link href="/evaluate">
              <Button icon={<PenSquare className="w-4 h-4" />} size="lg">
                Start Your First Evaluation
              </Button>
            </Link>
          </div>
        </Card>
      )}
    </div>
  );
}
