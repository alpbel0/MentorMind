'use client';

import { Card, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { GenerateQuestionResponse } from '@/types';
import { MessageSquare, Bot, Tag, FileQuestion } from 'lucide-react';

interface QuestionDisplayProps {
  data: GenerateQuestionResponse;
}

export function QuestionDisplay({ data }: QuestionDisplayProps) {
  return (
    <div className="space-y-6">
      {/* Question Card */}
      <Card>
        <CardHeader
          title="Question"
          subtitle="The question posed to the AI model"
          action={
            <div className="flex gap-2">
              <Badge variant="info">{data.category}</Badge>
              {data.question_type && (
                <Badge variant="default">{data.question_type.replace('_', ' ')}</Badge>
              )}
            </div>
          }
        />
        <div className="flex items-start gap-4">
          <div className="p-2 bg-indigo-100 rounded-lg">
            <FileQuestion className="w-5 h-5 text-indigo-600" />
          </div>
          <p className="text-slate-700 leading-relaxed flex-1">{data.question}</p>
        </div>
      </Card>

      {/* Model Response Card */}
      <Card>
        <CardHeader
          title="Model Response"
          subtitle={`Response from ${data.model_name}`}
          action={
            <Badge variant="default">
              <Bot className="w-3 h-3 mr-1" />
              {data.model_name.split('/').pop()}
            </Badge>
          }
        />
        <div className="flex items-start gap-4">
          <div className="p-2 bg-emerald-100 rounded-lg">
            <MessageSquare className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="flex-1">
            <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">
              {data.model_response}
            </p>
          </div>
        </div>
      </Card>

      {/* Metadata */}
      <div className="flex items-center gap-4 text-sm text-slate-500">
        <span className="flex items-center gap-1">
          <Tag className="w-4 h-4" />
          Question ID: <code className="font-mono text-xs">{data.question_id}</code>
        </span>
        <span className="flex items-center gap-1">
          <MessageSquare className="w-4 h-4" />
          Response ID: <code className="font-mono text-xs">{data.response_id}</code>
        </span>
      </div>
    </div>
  );
}
