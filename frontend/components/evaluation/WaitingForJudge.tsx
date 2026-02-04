'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/ui/Card';
import { Spinner } from '@/components/ui/Spinner';
import { Button } from '@/components/ui/Button';
import { usePolling } from '@/hooks/usePolling';
import { getFeedback } from '@/lib/api';
import { FeedbackResponse } from '@/types';
import { Brain, CheckCircle, Clock, RefreshCw } from 'lucide-react';

interface WaitingForJudgeProps {
  evaluationId: string;
}

export function WaitingForJudge({ evaluationId }: WaitingForJudgeProps) {
  const router = useRouter();
  const [dots, setDots] = useState('');

  const { data, error, isPolling, refetch } = usePolling<FeedbackResponse>({
    fetcher: () => getFeedback(evaluationId),
    interval: 3000,
    shouldStop: (data) => data.status !== 'processing',
    onSuccess: (data) => {
      if (data.status !== 'processing') {
        router.push(`/feedback/${evaluationId}`);
      }
    },
  });

  // Animate dots
  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? '' : prev + '.'));
    }, 500);
    return () => clearInterval(interval);
  }, []);

  const stages = [
    { id: 1, label: 'Evaluation Submitted', completed: true },
    { id: 2, label: 'Stage 1: Independent Analysis', completed: false },
    { id: 3, label: 'Stage 2: Comparison & Feedback', completed: false },
  ];

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <div className="text-center py-8">
          {/* Icon */}
          <div className="relative inline-flex items-center justify-center mb-6">
            <div className="absolute inset-0 bg-indigo-100 rounded-full animate-ping opacity-25" />
            <div className="relative p-4 bg-indigo-100 rounded-full">
              <Brain className="w-12 h-12 text-indigo-600" />
            </div>
          </div>

          {/* Title */}
          <h2 className="text-2xl font-bold text-slate-900 mb-2">
            GPT-4o is Evaluating{dots}
          </h2>
          <p className="text-slate-500 mb-8">
            The judge model is analyzing your evaluation. This usually takes 10-30 seconds.
          </p>

          {/* Progress Steps */}
          <div className="flex flex-col items-start max-w-xs mx-auto mb-8">
            {stages.map((stage, index) => (
              <div key={stage.id} className="flex items-center w-full">
                <div className="flex items-center">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      stage.completed
                        ? 'bg-emerald-100 text-emerald-600'
                        : index === 1 && isPolling
                        ? 'bg-indigo-100 text-indigo-600'
                        : 'bg-slate-100 text-slate-400'
                    }`}
                  >
                    {stage.completed ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : index === 1 && isPolling ? (
                      <Spinner size="sm" />
                    ) : (
                      <Clock className="w-4 h-4" />
                    )}
                  </div>
                  <span
                    className={`ml-3 text-sm ${
                      stage.completed || (index === 1 && isPolling)
                        ? 'text-slate-900 font-medium'
                        : 'text-slate-400'
                    }`}
                  >
                    {stage.label}
                  </span>
                </div>
                {index < stages.length - 1 && (
                  <div className="w-px h-6 bg-slate-200 ml-4 my-1" />
                )}
              </div>
            ))}
          </div>

          {/* Evaluation ID */}
          <div className="bg-slate-50 rounded-lg p-3 mb-6">
            <p className="text-xs text-slate-500">Evaluation ID</p>
            <code className="text-sm font-mono text-slate-700">{evaluationId}</code>
          </div>

          {/* Error State */}
          {error && (
            <div className="mb-6 p-4 bg-rose-50 text-rose-700 rounded-lg text-sm">
              {error.message}
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-center gap-4">
            <Button
              variant="outline"
              onClick={() => refetch()}
              icon={<RefreshCw className="w-4 h-4" />}
            >
              Check Status
            </Button>
            <Button
              variant="ghost"
              onClick={() => router.push('/')}
            >
              Return to Dashboard
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
