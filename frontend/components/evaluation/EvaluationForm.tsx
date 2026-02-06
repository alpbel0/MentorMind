'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { MetricScoreCard } from './MetricScoreCard';
import { MetricName, EvaluationsRecord, MetricEvaluation, GenerateQuestionResponse } from '@/types';
import { METRICS } from '@/lib/constants';
import { Send, AlertCircle, ArrowLeft, ArrowRight, CheckCircle2 } from 'lucide-react';

interface EvaluationFormProps {
  questionData: GenerateQuestionResponse;
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

export function EvaluationForm({ questionData, onSubmit, isSubmitting }: EvaluationFormProps) {
  const [evaluations, setEvaluations] = useState<EvaluationsRecord>(initialEvaluations);
  const [errors, setErrors] = useState<string[]>([]);
  const [currentMetricIndex, setCurrentMetricIndex] = useState(0);
  const [validatedIndices, setValidatedIndices] = useState<Set<number>>(new Set());

  const currentMetric = METRICS[currentMetricIndex];

  const handleMetricChange = (metric: MetricName, value: MetricEvaluation) => {
    setEvaluations((prev) => ({
      ...prev,
      [metric]: value,
    }));

    // Mark current index as potentially validated (will be checked on navigation)
    if (value.score !== null && value.reasoning.trim()) {
      setValidatedIndices((prev) => new Set(prev).add(currentMetricIndex));
    } else {
      setValidatedIndices((prev) => {
        const next = new Set(prev);
        next.delete(currentMetricIndex);
        return next;
      });
    }
  };

  const validateCurrentMetric = (): boolean => {
    const eval_ = evaluations[currentMetric];
    const newErrors: string[] = [];

    if (!eval_.reasoning.trim()) {
      newErrors.push(`${currentMetric}: Reasoning is required`);
    }
    if (eval_.score !== null && (eval_.score < 1 || eval_.score > 5)) {
      newErrors.push(`${currentMetric}: Score must be between 1 and 5`);
    }

    if (newErrors.length > 0) {
      setErrors(newErrors);
      return false;
    }

    setErrors([]);
    return true;
  };

  const handleNext = () => {
    if (!validateCurrentMetric()) return;

    if (currentMetricIndex < METRICS.length - 1) {
      setCurrentMetricIndex((i) => i + 1);
      setErrors([]);
    }
  };

  const handlePrevious = () => {
    if (currentMetricIndex > 0) {
      setCurrentMetricIndex((i) => i - 1);
      setErrors([]);
    }
  };

  const handleMetricSelect = (index: number) => {
    setCurrentMetricIndex(index);
    setErrors([]);
  };

  const validateAndSubmit = () => {
    if (!validateCurrentMetric()) return;

    const newErrors: string[] = [];

    // Check all metrics have reasoning
    METRICS.forEach((metric) => {
      const eval_ = evaluations[metric];
      if (!eval_.reasoning.trim()) {
        newErrors.push(`${metric}: Reasoning is required`);
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
  const isLastMetric = currentMetricIndex === METRICS.length - 1;

  return (
    <div className="space-y-6">
      {/* Overall Progress Indicator */}
      <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
        <div className="text-sm text-slate-600">
          <span className="font-medium">{scoredCount}/8</span> metrics scored
        </div>
        <div className="text-sm text-slate-600">
          <span className="font-medium">{reasonedCount}/8</span> reasonings provided
        </div>
        <div className="text-sm text-slate-600">
          Step <span className="font-medium">{currentMetricIndex + 1}</span> of {METRICS.length}
        </div>
      </div>

      {/* Progress Bar - Clickable */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-500 px-1">
          <span>Progress</span>
          <span>{Math.round(((currentMetricIndex + 1) / METRICS.length) * 100)}%</span>
        </div>
        <div className="flex gap-1">
          {METRICS.map((metric, index) => {
            const isCompleted = index < currentMetricIndex;
            const isCurrent = index === currentMetricIndex;
            const isValidated = validatedIndices.has(index);

            return (
              <button
                key={metric}
                type="button"
                onClick={() => handleMetricSelect(index)}
                className={`
                  flex-1 h-2 rounded-full transition-all duration-300 relative group
                  ${isCompleted
                    ? 'bg-emerald-500'
                    : isCurrent
                    ? 'bg-indigo-600'
                    : 'bg-slate-200'
                  }
                  ${isValidated && !isCompleted ? 'ring-2 ring-emerald-300 ring-offset-1' : ''}
                `}
                title={`${metric}${isValidated ? ' ✓' : ''}`}
              >
                {/* Tooltip */}
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-slate-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
                  <div className="flex items-center gap-1">
                    {metric}
                    {isValidated && <CheckCircle2 className="w-3 h-3 text-emerald-400" />}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
        {/* Current metric label */}
        <div className="text-center">
          <span className="text-sm font-medium text-indigo-600">
            {currentMetric}
          </span>
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

      {/* Single Metric Card - Full Width */}
      <MetricScoreCard
        key={currentMetric}
        metric={currentMetric}
        value={evaluations[currentMetric]}
        onChange={(value) => handleMetricChange(currentMetric, value)}
      />

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-200">
        <Button
          variant="outline"
          onClick={handlePrevious}
          disabled={currentMetricIndex === 0}
          icon={<ArrowLeft className="w-4 h-4" />}
        >
          Previous
        </Button>

        {isLastMetric ? (
          <Button
            onClick={validateAndSubmit}
            isLoading={isSubmitting}
            icon={<Send className="w-4 h-4" />}
            size="lg"
            className="bg-indigo-600 hover:bg-indigo-700"
          >
            Submit Evaluation
          </Button>
        ) : (
          <Button
            onClick={handleNext}
          >
            Next Metric
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        )}
      </div>

      {/* Quick navigation dots */}
      <div className="flex justify-center gap-2 flex-wrap">
        {METRICS.map((metric, index) => (
          <button
            key={metric}
            type="button"
            onClick={() => handleMetricSelect(index)}
            className={`
              w-3 h-3 rounded-full transition-all duration-200
              ${index === currentMetricIndex
                ? 'bg-indigo-600 scale-125'
                : validatedIndices.has(index)
                ? 'bg-emerald-500'
                : 'bg-slate-300 hover:bg-slate-400'
              }
            `}
            title={metric}
          />
        ))}
      </div>
    </div>
  );
}
