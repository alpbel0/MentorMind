'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { MetricName, MetricEvaluation } from '@/types';
import { METRIC_COLORS_LIGHT, METRIC_DESCRIPTIONS, SCORE_COLORS, SCORE_COLORS_BORDER, SCORE_COLORS_LIGHT } from '@/lib/constants';
import { CheckCircle, XCircle } from 'lucide-react';

interface MetricScoreCardProps {
  metric: MetricName;
  value: MetricEvaluation;
  onChange: (value: MetricEvaluation) => void;
}

export function MetricScoreCard({ metric, value, onChange }: MetricScoreCardProps) {
  const [isNA, setIsNA] = useState(value.score === null);
  const localScore = value.score;
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

  const scoreButtons = [
    { value: 1, color: SCORE_COLORS[1], hover: 'hover:bg-rose-100' },
    { value: 2, color: SCORE_COLORS[2], hover: 'hover:bg-orange-100' },
    { value: 3, color: SCORE_COLORS[3], hover: 'hover:bg-amber-100' },
    { value: 4, color: SCORE_COLORS[4], hover: 'hover:bg-emerald-100' },
    { value: 5, color: SCORE_COLORS[5], hover: 'hover:bg-green-100' },
  ];

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

        {/* Segmented Control Score Selector */}
        {!isNA && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-500 px-1">
              <span className="text-rose-600 font-medium">Very Poor</span>
              <span className="text-green-600 font-medium">Excellent</span>
            </div>
            <div className="flex rounded-lg overflow-hidden border-2 border-slate-200 dark:border-slate-700">
              {scoreButtons.map(({ value: scoreValue, color, hover }) => (
                <button
                  key={scoreValue}
                  type="button"
                  onClick={() => handleScoreChange(scoreValue)}
                  className={`
                    flex-1 py-3 px-2 text-lg font-semibold transition-all duration-200 relative
                    ${localScore === scoreValue
                      ? `${color} text-white shadow-lg scale-105`
                      : `bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 ${hover}`
                    }
                    ${localScore !== scoreValue ? 'border-r border-slate-200 dark:border-slate-700 last:border-r-0' : ''}
                  `}
                >
                  {scoreValue}
                </button>
              ))}
            </div>
            {/* Score Feedback */}
            {localScore && (
              <div className="flex items-center justify-center gap-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div className={`w-3 h-3 rounded-full ${SCORE_COLORS[localScore]} animate-pulse`} />
                <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
                  Puan: {localScore}/5
                </span>
              </div>
            )}
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
            className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none dark:bg-slate-800 dark:border-slate-600 dark:text-slate-100"
            rows={2}
          />
        </div>
      </div>
    </Card>
  );
}
