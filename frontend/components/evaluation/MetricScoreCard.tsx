'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { MetricName, MetricEvaluation } from '@/types';
import { METRIC_COLORS_LIGHT, METRIC_DESCRIPTIONS } from '@/lib/constants';
import { CheckCircle, XCircle } from 'lucide-react';

interface MetricScoreCardProps {
  metric: MetricName;
  value: MetricEvaluation;
  onChange: (value: MetricEvaluation) => void;
}

export function MetricScoreCard({ metric, value, onChange }: MetricScoreCardProps) {
  const [isNA, setIsNA] = useState(value.score === null);
  const colorClasses = METRIC_COLORS_LIGHT[metric];

  const handleScoreChange = (score: number) => {
    setIsNA(false);
    onChange({ ...value, score });
  };

  const handleNAToggle = () => {
    const newIsNA = !isNA;
    setIsNA(newIsNA);
    onChange({ ...value, score: newIsNA ? null : 3 });
  };

  const handleReasoningChange = (reasoning: string) => {
    onChange({ ...value, reasoning });
  };

  return (
    <Card className={`${isNA ? 'opacity-60' : ''}`}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h4 className="font-semibold text-slate-900">{metric}</h4>
            <p className="text-xs text-slate-500 mt-0.5">
              {METRIC_DESCRIPTIONS[metric]}
            </p>
          </div>
          <button
            onClick={handleNAToggle}
            className={`flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium transition-colors ${
              isNA
                ? 'bg-slate-200 text-slate-700'
                : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
            }`}
          >
            {isNA ? <XCircle className="w-3 h-3" /> : null}
            N/A
          </button>
        </div>

        {/* Score Selector */}
        {!isNA && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span>Very Poor</span>
              <span>Excellent</span>
            </div>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((score) => (
                <button
                  key={score}
                  onClick={() => handleScoreChange(score)}
                  className={`flex-1 py-3 rounded-lg font-semibold text-lg transition-all ${
                    value.score === score
                      ? `${colorClasses} ring-2 ring-offset-2 ring-current`
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {score}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Reasoning */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Reasoning {!isNA && <span className="text-rose-500">*</span>}
          </label>
          <textarea
            value={value.reasoning}
            onChange={(e) => handleReasoningChange(e.target.value)}
            placeholder={
              isNA
                ? 'Explain why this metric is not applicable...'
                : 'Explain your score...'
            }
            className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
            rows={2}
          />
        </div>
      </div>
    </Card>
  );
}
