'use client';

import { META_SCORE_LABELS, META_SCORE_COLORS } from '@/lib/constants';

interface MetaScoreGaugeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

const sizeClasses = {
  sm: { container: 'w-20 h-20', text: 'text-xl', label: 'text-xs' },
  md: { container: 'w-32 h-32', text: 'text-3xl', label: 'text-sm' },
  lg: { container: 'w-40 h-40', text: 'text-4xl', label: 'text-base' },
};

export function MetaScoreGauge({
  score,
  size = 'md',
  showLabel = true,
}: MetaScoreGaugeProps) {
  const percentage = (score / 5) * 100;
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;
  const classes = sizeClasses[size];

  // Get color based on score
  const getColor = (score: number) => {
    if (score >= 4.5) return '#22c55e'; // green-500
    if (score >= 3.5) return '#10b981'; // emerald-500
    if (score >= 2.5) return '#f59e0b'; // amber-500
    if (score >= 1.5) return '#f97316'; // orange-500
    return '#ef4444'; // red-500
  };

  return (
    <div className="flex flex-col items-center">
      <div className={`relative ${classes.container}`}>
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="8"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke={getColor(score)}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-700 ease-out"
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`${classes.text} font-bold ${META_SCORE_COLORS[Math.round(score)] || 'text-slate-600'}`}>
            {score.toFixed(1)}
          </span>
          <span className="text-xs text-slate-400">/5</span>
        </div>
      </div>
      {showLabel && (
        <span className={`mt-2 font-medium text-slate-600 ${classes.label}`}>
          {META_SCORE_LABELS[Math.round(score)] || 'N/A'}
        </span>
      )}
    </div>
  );
}
