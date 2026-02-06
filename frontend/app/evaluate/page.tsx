'use client';

import { useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingState } from '@/components/ui/Spinner';
import {
  MetricSelector,
  QuestionDisplay,
  EvaluationForm,
  WaitingForJudge,
} from '@/components/evaluation';
import { generateQuestion, submitEvaluation } from '@/lib/api';
import {
  MetricName,
  GenerateQuestionResponse,
  EvaluationsRecord,
} from '@/types';
import { ArrowLeft, ArrowRight, Sparkles, RefreshCw } from 'lucide-react';

type Step = 'select_metric' | 'view_question' | 'evaluate' | 'waiting';

function EvaluateContent() {
  const searchParams = useSearchParams();
  const usePool = searchParams.get('pool') === 'true';

  const [step, setStep] = useState<Step>('select_metric');
  const [selectedMetric, setSelectedMetric] = useState<MetricName | null>(null);
  const [questionData, setQuestionData] = useState<GenerateQuestionResponse | null>(null);
  const [evaluationId, setEvaluationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleMetricSelect = (metric: MetricName) => {
    setSelectedMetric(metric);
    setError(null);
  };

  const handleGenerateQuestion = async () => {
    if (!selectedMetric) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await generateQuestion(selectedMetric, usePool);
      setQuestionData(data);
      setStep('view_question');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate question');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProceedToEvaluate = () => {
    setStep('evaluate');
  };

  const handleSubmitEvaluation = async (evaluations: EvaluationsRecord) => {
    if (!questionData) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await submitEvaluation(questionData.response_id, evaluations);
      setEvaluationId(result.evaluation_id);
      setStep('waiting');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit evaluation');
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setStep('select_metric');
    setSelectedMetric(null);
    setQuestionData(null);
    setEvaluationId(null);
    setError(null);
  };

  // Step indicator
  const steps = [
    { id: 'select_metric', label: 'Select Metric' },
    { id: 'view_question', label: 'View Question' },
    { id: 'evaluate', label: 'Evaluate' },
    { id: 'waiting', label: 'Get Feedback' },
  ];

  const currentStepIndex = steps.findIndex((s) => s.id === step);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Progress Steps */}
      <div className="flex items-center justify-between mb-8">
        {steps.map((s, index) => (
          <div key={s.id} className="flex items-center">
            <div
              className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                index < currentStepIndex
                  ? 'bg-emerald-100 text-emerald-700'
                  : index === currentStepIndex
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 text-slate-400'
              }`}
            >
              {index + 1}
            </div>
            <span
              className={`ml-2 text-sm ${
                index <= currentStepIndex ? 'text-slate-900 font-medium' : 'text-slate-400'
              }`}
            >
              {s.label}
            </span>
            {index < steps.length - 1 && (
              <div
                className={`w-12 h-0.5 mx-4 ${
                  index < currentStepIndex ? 'bg-emerald-400' : 'bg-slate-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-700">
          {error}
        </div>
      )}

      {/* Step: Select Metric */}
      {step === 'select_metric' && (
        <div className="space-y-6">
          <Card>
            <CardHeader
              title="Select Primary Metric"
              subtitle="Choose the metric you want to focus on for this evaluation"
            />
            <MetricSelector
              selectedMetric={selectedMetric}
              onSelect={handleMetricSelect}
            />
          </Card>

          {/* Mode indicator */}
          <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <Sparkles className="w-4 h-4" />
              {usePool ? 'Using questions from pool' : 'Generating new question'}
            </div>
          </div>

          <div className="flex justify-end">
            <Button
              onClick={handleGenerateQuestion}
              disabled={!selectedMetric}
              isLoading={isLoading}
              icon={<ArrowRight className="w-4 h-4" />}
              size="lg"
            >
              Generate Question
            </Button>
          </div>
        </div>
      )}

      {/* Step: View Question */}
      {step === 'view_question' && questionData && (
        <div className="space-y-6">
          <QuestionDisplay data={questionData} />

          <div className="flex justify-between">
            <Button variant="outline" onClick={handleReset} icon={<ArrowLeft className="w-4 h-4" />}>
              Start Over
            </Button>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={handleGenerateQuestion}
                isLoading={isLoading}
                icon={<RefreshCw className="w-4 h-4" />}
              >
                New Question
              </Button>
              <Button
                onClick={handleProceedToEvaluate}
                icon={<ArrowRight className="w-4 h-4" />}
                size="lg"
              >
                Proceed to Evaluation
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Step: Evaluate */}
      {step === 'evaluate' && questionData && (
        <div className="space-y-6">
          {/* Full QuestionDisplay - always visible for reference */}
          <QuestionDisplay data={questionData} />

          {/* Evaluation Form */}
          <Card>
            <CardHeader
              title="Evaluate the Response"
              subtitle="Score each metric and provide your reasoning"
            />
            <EvaluationForm
              questionData={questionData}
              onSubmit={handleSubmitEvaluation}
              isSubmitting={isLoading}
            />
          </Card>

          <div className="flex justify-start">
            <Button
              variant="outline"
              onClick={() => setStep('view_question')}
              icon={<ArrowLeft className="w-4 h-4" />}
            >
              Back to Question View
            </Button>
          </div>
        </div>
      )}

      {/* Step: Waiting for Judge */}
      {step === 'waiting' && evaluationId && (
        <WaitingForJudge evaluationId={evaluationId} />
      )}

      {/* Loading State */}
      {isLoading && step === 'select_metric' && (
        <div className="fixed inset-0 bg-white/80 flex items-center justify-center z-50">
          <LoadingState message="Generating question..." />
        </div>
      )}
    </div>
  );
}

export default function EvaluatePage() {
  return (
    <Suspense fallback={<LoadingState message="Loading..." />}>
      <EvaluateContent />
    </Suspense>
  );
}
