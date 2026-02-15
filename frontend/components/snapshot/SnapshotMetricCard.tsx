'use client';

import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { EvidenceItem } from '@/types';
import { slugToDisplay, SLUG_COLORS_LIGHT } from '@/lib/constants';
import type { MetricSlug } from '@/types';
import { CheckCircle, AlertTriangle, XCircle, ArrowRight, FileSearch } from 'lucide-react';

interface SnapshotMetricCardProps {
  metricSlug: string;
  userScore: number | null;
  judgeScore: number | null;
  evidenceItems: EvidenceItem[];
  onViewEvidence: () => void;
}

export function SnapshotMetricCard({
  metricSlug,
  userScore,
  judgeScore,
  evidenceItems,
  onViewEvidence,
}: SnapshotMetricCardProps) {
  const gap = userScore != null && judgeScore != null ? Math.abs(userScore - judgeScore) : null;
  const colorClasses = SLUG_COLORS_LIGHT[metricSlug as MetricSlug] || 'bg-slate-100 text-slate-700 border-slate-200';

  const formatScore = (score: number | null) => (score === null ? 'N/A' : String(score));

  const getGapIcon = () => {
    if (gap === null) return null;
    if (gap === 0) return <CheckCircle className="w-4 h-4 text-emerald-500" />;
    if (gap <= 1) return <AlertTriangle className="w-4 h-4 text-amber-500" />;
    return <XCircle className="w-4 h-4 text-rose-500" />;
  };

  return (
    <Card className="overflow-hidden" padding="none">
      {/* Header */}
      <div className={`px-4 py-3 ${colorClasses.split(' ')[0]} border-b border-slate-100`}>
        <div className="flex items-center justify-between">
          <h4 className={`font-semibold text-sm ${colorClasses.split(' ')[1]}`}>
            {slugToDisplay(metricSlug)}
          </h4>
          {gap !== null && (
            <span className="flex items-center gap-1">
              {getGapIcon()}
              <span
                className={`text-xs font-mono font-bold ${
                  gap === 0 ? 'text-emerald-600' : gap <= 1 ? 'text-amber-600' : 'text-rose-600'
                }`}
              >
                {gap === 0 ? '✓' : `±${gap}`}
              </span>
            </span>
          )}
        </div>
      </div>

      {/* Scores */}
      <div className="p-4">
        <div className="flex items-center justify-center gap-4 mb-3">
          <div className="text-center">
            <p className="text-[10px] text-slate-400 mb-1">Sen</p>
            <div
              className={`w-10 h-10 rounded-lg flex items-center justify-center text-lg font-bold ${
                userScore === null ? 'bg-slate-50 text-slate-300' : 'bg-indigo-50 text-indigo-700'
              }`}
            >
              {formatScore(userScore)}
            </div>
          </div>

          <ArrowRight className="w-4 h-4 text-slate-300" />

          <div className="text-center">
            <p className="text-[10px] text-slate-400 mb-1">Judge</p>
            <div
              className={`w-10 h-10 rounded-lg flex items-center justify-center text-lg font-bold ${
                judgeScore === null ? 'bg-slate-50 text-slate-300' : 'bg-emerald-50 text-emerald-700'
              }`}
            >
              {formatScore(judgeScore)}
            </div>
          </div>
        </div>

        {/* Evidence Button */}
        {evidenceItems.length > 0 ? (
          <button
            onClick={onViewEvidence}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium text-amber-700 bg-amber-50 hover:bg-amber-100 rounded-lg transition-colors"
          >
            <FileSearch className="w-3.5 h-3.5" />
            Kanıt Gör ({evidenceItems.length})
          </button>
        ) : (
          <div className="text-center text-[10px] text-slate-300 py-2">Kanıt yok</div>
        )}
      </div>
    </Card>
  );
}
