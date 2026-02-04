'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { LoadingState } from '@/components/ui/Spinner';
import { FeedbackPanel } from '@/components/feedback';
import { getFeedback } from '@/lib/api';
import { FeedbackResponse } from '@/types';
import { ArrowLeft, PenSquare, Home, RefreshCw } from 'lucide-react';

export default function FeedbackPage() {
  const params = useParams();
  const router = useRouter();
  const evaluationId = params.id as string;

  const [feedback, setFeedback] = useState<FeedbackResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFeedback = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getFeedback(evaluationId);
      
      // If still processing, show a message
      if (data.status === 'processing') {
        setError('Judge evaluation is still in progress. Please wait...');
        setFeedback(null);
      } else {
        setFeedback(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load feedback');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFeedback();
  }, [evaluationId]);

  if (isLoading) {
    return <LoadingState message="Loading feedback..." />;
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl">
          <p className="text-amber-700">{error}</p>
        </div>
        <div className="flex justify-center gap-4">
          <Button
            variant="outline"
            onClick={fetchFeedback}
            icon={<RefreshCw className="w-4 h-4" />}
          >
            Retry
          </Button>
          <Link href="/">
            <Button variant="ghost" icon={<Home className="w-4 h-4" />}>
              Go to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  if (!feedback) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <p className="text-slate-500 mb-4">No feedback data available</p>
        <Link href="/">
          <Button icon={<Home className="w-4 h-4" />}>Go to Dashboard</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={() => router.back()}
          icon={<ArrowLeft className="w-4 h-4" />}
        >
          Back
        </Button>
        <div className="flex gap-3">
          <Link href="/history">
            <Button variant="outline">View All Evaluations</Button>
          </Link>
          <Link href="/evaluate">
            <Button icon={<PenSquare className="w-4 h-4" />}>
              New Evaluation
            </Button>
          </Link>
        </div>
      </div>

      {/* Feedback Content */}
      <FeedbackPanel feedback={feedback} />
    </div>
  );
}
