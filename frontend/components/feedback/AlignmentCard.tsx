'use client';

import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { MetricName, AlignmentAnalysis } from '@/types';
import { METRIC_COLORS_LIGHT, VERDICT_COLORS, VERDICT_LABELS } from '@/lib/constants';
import { ArrowRight, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

interface AlignmentCardProps {
  metric: MetricName;
  analysis: AlignmentAnalysis;
}

export function AlignmentCard({ metric, analysis }: AlignmentCardProps) {
  const colorClasses = METRIC_COLORS_LIGHT[metric];
  const verdictClasses = VERDICT_COLORS[analysis.verdict] || VERDICT_COLORS.aligned;

  const getVerdictIcon = () => {
    if (analysis.verdict === 'aligned') {
      return <CheckCircle className="w-4 h-4 text-emerald-600" />;
    }
    if (analysis.verdict.includes('significantly')) {
      return <XCircle className="w-4 h-4 text-rose-600" />;
    }
    return <AlertTriangle className="w-4 h-4 text-amber-600" />;
  };

  const formatScore = (score: number | null) => {
    if (score === null) return 'N/A';
    return score.toString();
  };

  return (
    <Card className="overflow-hidden">
      {/* Header */}
      <div className={`px-4 py-3 ${colorClasses.split(' ')[0]} border-b border-slate-100`}>
        <div className="flex items-center justify-between">
          <h4 className={`font-semibold ${colorClasses.split(' ')[1]}`}>{metric}</h4>
          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${verdictClasses}`}>
            {getVerdictIcon()}
            {VERDICT_LABELS[analysis.verdict] || analysis.verdict}
          </span>
        </div>
      </div>

      {/* Score Comparison */}
      <div className="p-4">
        <div className="flex items-center justify-center gap-4 mb-4">
          {/* User Score */}
          <div className="text-center">
            <p className="text-xs text-slate-500 mb-1">Your Score</p>
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl font-bold ${
              analysis.user_score === null ? 'bg-slate-100 text-slate-400' : 'bg-indigo-100 text-indigo-700'
            }`}>
              {formatScore(analysis.user_score)}
            </div>
          </div>

          {/* Arrow */}
          <div className="flex flex-col items-center">
            <ArrowRight className="w-5 h-5 text-slate-300" />
            <span className={`text-xs font-mono ${
              analysis.gap === 0 ? 'text-emerald-600' : 
              Math.abs(analysis.gap) <= 1 ? 'text-amber-600' : 'text-rose-600'
            }`}>
              {analysis.gap === 0 ? '=' : analysis.gap > 0 ? `+${analysis.gap}` : analysis.gap}
            </span>
          </div>

          {/* Judge Score */}
          <div className="text-center">
            <p className="text-xs text-slate-500 mb-1">Judge Score</p>
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl font-bold ${
              analysis.judge_score === null ? 'bg-slate-100 text-slate-400' : 'bg-emerald-100 text-emerald-700'
            }`}>
              {formatScore(analysis.judge_score)}
            </div>
          </div>
        </div>

        {/* Feedback */}
        <div className="pt-3 border-t border-slate-100">
          <p className="text-sm text-slate-600">{analysis.feedback}</p>
        </div>
      </div>
    </Card>
  );
}
