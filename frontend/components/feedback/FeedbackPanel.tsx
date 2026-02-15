'use client';

import Link from 'next/link';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FeedbackResponse, MetricName } from '@/types';
import { MetaScoreGauge } from '@/components/stats/MetaScoreGauge';
import { AlignmentCard } from './AlignmentCard';
import { METRICS } from '@/lib/constants';
import {
  MessageSquare,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  AlertCircle,
  History,
  BookOpen,
} from 'lucide-react';

interface FeedbackPanelProps {
  feedback: FeedbackResponse;
}

export function FeedbackPanel({ feedback }: FeedbackPanelProps) {
  return (
    <div className="space-y-6">
      {/* Snapshot Link */}
      <div className="flex items-center justify-end">
        <Link href="/snapshots">
          <Button variant="outline" size="sm" icon={<BookOpen className="w-4 h-4" />}>
            Snapshot Detaylarını Gör
          </Button>
        </Link>
      </div>

      {/* Top Section: Meta Score + Overall Feedback */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Meta Score */}
        <Card className="flex flex-col items-center justify-center py-8">
          <h3 className="text-sm font-medium text-slate-500 mb-4">Evaluation Quality</h3>
          <MetaScoreGauge score={feedback.judge_meta_score || 0} size="lg" />
        </Card>

        {/* Overall Feedback */}
        <Card className="lg:col-span-2">
          <CardHeader
            title="Overall Feedback"
            subtitle="Summary from GPT-4o Judge"
          />
          <div className="flex items-start gap-3">
            <div className="p-2 bg-indigo-100 rounded-lg">
              <MessageSquare className="w-5 h-5 text-indigo-600" />
            </div>
            <p className="text-slate-700 leading-relaxed">
              {feedback.overall_feedback}
            </p>
          </div>
        </Card>
      </div>

      {/* Alignment Analysis Grid */}
      <Card>
        <CardHeader
          title="Metric Alignment Analysis"
          subtitle="Comparison between your scores and judge scores"
        />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {METRICS.map((metric) => {
            const analysis = feedback.alignment_analysis?.[metric];
            if (!analysis) return null;
            return (
              <AlignmentCard
                key={metric}
                metric={metric}
                analysis={analysis}
              />
            );
          })}
        </div>
      </Card>

      {/* Improvement Areas & Positive Feedback */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Improvement Areas */}
        <Card>
          <CardHeader
            title="Areas for Improvement"
            subtitle="Focus on these to improve your evaluation skills"
          />
          {feedback.improvement_areas && feedback.improvement_areas.length > 0 ? (
            <ul className="space-y-3">
              {feedback.improvement_areas.map((area, index) => (
                <li key={index} className="flex items-start gap-3">
                  <div className="p-1 bg-amber-100 rounded">
                    <TrendingDown className="w-4 h-4 text-amber-600" />
                  </div>
                  <span className="text-sm text-slate-700">{area}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="flex items-center gap-3 text-emerald-600">
              <CheckCircle className="w-5 h-5" />
              <span className="text-sm">No specific improvement areas identified!</span>
            </div>
          )}
        </Card>

        {/* Positive Feedback */}
        <Card>
          <CardHeader
            title="What You Did Well"
            subtitle="Strengths in your evaluation"
          />
          {feedback.positive_feedback && feedback.positive_feedback.length > 0 ? (
            <ul className="space-y-3">
              {feedback.positive_feedback.map((item, index) => (
                <li key={index} className="flex items-start gap-3">
                  <div className="p-1 bg-emerald-100 rounded">
                    <TrendingUp className="w-4 h-4 text-emerald-600" />
                  </div>
                  <span className="text-sm text-slate-700">{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="flex items-center gap-3 text-slate-400">
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm">No specific positive feedback</span>
            </div>
          )}
        </Card>
      </div>

      {/* Past Patterns */}
      {feedback.past_patterns_referenced && feedback.past_patterns_referenced.length > 0 && (
        <Card>
          <CardHeader
            title="Past Patterns Referenced"
            subtitle="Similar patterns from your previous evaluations"
          />
          <div className="flex flex-wrap gap-2">
            {feedback.past_patterns_referenced.map((pattern, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-1 px-3 py-1.5 bg-slate-100 text-slate-600 text-sm rounded-lg"
              >
                <History className="w-3 h-3" />
                {pattern}
              </span>
            ))}
          </div>
        </Card>
      )}

      {/* Evaluation ID */}
      <div className="text-center text-sm text-slate-400">
        Evaluation ID: <code className="font-mono">{feedback.evaluation_id}</code>
      </div>
    </div>
  );
}
