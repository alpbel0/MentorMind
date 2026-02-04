'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  ClipboardCheck,
  TrendingUp,
  Target,
  ArrowRight,
  Activity,
} from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingState } from '@/components/ui/Spinner';
import { StatsCard, MetaScoreGauge, MetricPerformanceChart } from '@/components/stats';
import { getStatsOverview } from '@/lib/api';
import { StatsOverviewResponse } from '@/types';

export default function DashboardPage() {
  const [stats, setStats] = useState<StatsOverviewResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchStats() {
      try {
        const data = await getStatsOverview();
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load stats');
      } finally {
        setIsLoading(false);
      }
    }
    fetchStats();
  }, []);

  if (isLoading) {
    return <LoadingState message="Loading dashboard..." />;
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <div className="text-rose-500 mb-4">
          <Activity className="w-12 h-12" />
        </div>
        <p className="text-slate-600 mb-4">{error}</p>
        <Button onClick={() => window.location.reload()}>Retry</Button>
      </div>
    );
  }

  const hasData = stats && stats.total_evaluations > 0;

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">
            Welcome to MentorMind
          </h2>
          <p className="text-slate-500 mt-1">
            Track your AI evaluation skills and improve with expert feedback
          </p>
        </div>
        <Link href="/evaluate">
          <Button icon={<ArrowRight className="w-4 h-4" />}>
            Start New Evaluation
          </Button>
        </Link>
      </div>

      {/* Stats Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Evaluations"
          value={stats?.total_evaluations || 0}
          subtitle="All time"
          icon={<ClipboardCheck className="w-6 h-6" />}
        />
        <StatsCard
          title="Average Meta Score"
          value={stats?.average_meta_score?.toFixed(1) || 'N/A'}
          subtitle="Out of 5.0"
          icon={<Target className="w-6 h-6" />}
        />
        <StatsCard
          title="Improvement Trend"
          value={stats?.improvement_trend || 'N/A'}
          subtitle="Last 10 evaluations"
          icon={<TrendingUp className="w-6 h-6" />}
        />
        <StatsCard
          title="Metrics Tracked"
          value={Object.keys(stats?.metrics_performance || {}).length}
          subtitle="Active metrics"
          icon={<Activity className="w-6 h-6" />}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Chart */}
        <Card className="lg:col-span-2">
          <CardHeader
            title="Metric Performance"
            subtitle="Average gap between your scores and judge scores"
          />
          {hasData ? (
            <MetricPerformanceChart data={stats.metrics_performance} />
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-slate-400">
              <Activity className="w-12 h-12 mb-3" />
              <p>Complete your first evaluation to see performance data</p>
            </div>
          )}
        </Card>

        {/* Meta Score Gauge */}
        <Card>
          <CardHeader
            title="Overall Score"
            subtitle="Your evaluation quality rating"
          />
          <div className="flex flex-col items-center justify-center py-4">
            {hasData ? (
              <MetaScoreGauge score={stats.average_meta_score} size="lg" />
            ) : (
              <div className="flex flex-col items-center justify-center h-48 text-slate-400">
                <Target className="w-12 h-12 mb-3" />
                <p className="text-center">No evaluations yet</p>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card hover onClick={() => window.location.href = '/evaluate'}>
          <div className="flex items-center">
            <div className="p-3 bg-indigo-100 rounded-xl">
              <ClipboardCheck className="w-6 h-6 text-indigo-600" />
            </div>
            <div className="ml-4">
              <h3 className="font-semibold text-slate-900">New Evaluation</h3>
              <p className="text-sm text-slate-500">Start a new AI response evaluation</p>
            </div>
            <ArrowRight className="w-5 h-5 text-slate-400 ml-auto" />
          </div>
        </Card>

        <Card hover onClick={() => window.location.href = '/history'}>
          <div className="flex items-center">
            <div className="p-3 bg-emerald-100 rounded-xl">
              <TrendingUp className="w-6 h-6 text-emerald-600" />
            </div>
            <div className="ml-4">
              <h3 className="font-semibold text-slate-900">View History</h3>
              <p className="text-sm text-slate-500">Review past evaluations</p>
            </div>
            <ArrowRight className="w-5 h-5 text-slate-400 ml-auto" />
          </div>
        </Card>

        <Card hover onClick={() => window.location.href = '/evaluate?pool=true'}>
          <div className="flex items-center">
            <div className="p-3 bg-amber-100 rounded-xl">
              <Target className="w-6 h-6 text-amber-600" />
            </div>
            <div className="ml-4">
              <h3 className="font-semibold text-slate-900">Practice Mode</h3>
              <p className="text-sm text-slate-500">Use questions from the pool</p>
            </div>
            <ArrowRight className="w-5 h-5 text-slate-400 ml-auto" />
          </div>
        </Card>
      </div>
    </div>
  );
}
