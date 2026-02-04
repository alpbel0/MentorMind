'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { MetricScoreCard } from './MetricScoreCard';
import { MetricName, EvaluationsRecord, MetricEvaluation } from '@/types';
import { METRICS } from '@/lib/constants';
import { Send, AlertCircle } from 'lucide-react';

interface EvaluationFormProps {
  onSubmit: (evaluations: EvaluationsRecord) => void;
  isSubmitting: boolean;
}

const initialEvaluations: EvaluationsRecord = METRICS.reduce(
  (acc, metric) => ({
    ...acc,
    [metric]: { score: null, reasoning: '' },
  }),
  {} as EvaluationsRecord
);

export function EvaluationForm({ onSubmit, isSubmitting }: EvaluationFormProps) {
  const [evaluations, setEvaluations] = useState<EvaluationsRecord>(initialEvaluations);
  const [errors, setErrors] = useState<string[]>([]);

  const handleMetricChange = (metric: MetricName, value: MetricEvaluation) => {
    setEvaluations((prev) => ({
      ...prev,
      [metric]: value,
    }));
  };

  const validateAndSubmit = () => {
    const newErrors: string[] = [];

    // Check that each metric has reasoning
    METRICS.forEach((metric) => {
      const eval_ = evaluations[metric];
      if (!eval_.reasoning.trim()) {
        newErrors.push(`${metric}: Reasoning is required`);
      }
      // If score is not null, it should be 1-5
      if (eval_.score !== null && (eval_.score < 1 || eval_.score > 5)) {
        newErrors.push(`${metric}: Score must be between 1 and 5`);
      }
    });

    // At least one metric should have a score
    const hasAtLeastOneScore = METRICS.some((m) => evaluations[m].score !== null);
    if (!hasAtLeastOneScore) {
      newErrors.push('At least one metric must have a score (not N/A)');
    }

    if (newErrors.length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors([]);
    onSubmit(evaluations);
  };

  const scoredCount = METRICS.filter((m) => evaluations[m].score !== null).length;
  const reasonedCount = METRICS.filter((m) => evaluations[m].reasoning.trim()).length;

  return (
    <div className="space-y-6">
      {/* Progress Indicator */}
      <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
        <div className="text-sm text-slate-600">
          <span className="font-medium">{scoredCount}/8</span> metrics scored
        </div>
        <div className="text-sm text-slate-600">
          <span className="font-medium">{reasonedCount}/8</span> reasonings provided
        </div>
      </div>

      {/* Errors */}
      {errors.length > 0 && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl">
          <div className="flex items-center gap-2 text-rose-700 font-medium mb-2">
            <AlertCircle className="w-4 h-4" />
            Please fix the following errors:
          </div>
          <ul className="list-disc list-inside text-sm text-rose-600 space-y-1">
            {errors.map((error, i) => (
              <li key={i}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {METRICS.map((metric) => (
          <MetricScoreCard
            key={metric}
            metric={metric}
            value={evaluations[metric]}
            onChange={(value) => handleMetricChange(metric, value)}
          />
        ))}
      </div>

      {/* Submit Button */}
      <div className="flex justify-end pt-4 border-t border-slate-200">
        <Button
          onClick={validateAndSubmit}
          isLoading={isSubmitting}
          icon={<Send className="w-4 h-4" />}
          size="lg"
        >
          Submit Evaluation
        </Button>
      </div>
    </div>
  );
}
