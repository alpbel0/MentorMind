// Evaluation Metrics
export type MetricName =
  | 'Truthfulness'
  | 'Helpfulness'
  | 'Safety'
  | 'Bias'
  | 'Clarity'
  | 'Consistency'
  | 'Efficiency'
  | 'Robustness';

export interface MetricEvaluation {
  score: number | null;
  reasoning: string;
}

export type EvaluationsRecord = Record<MetricName, MetricEvaluation>;

// API Request Types
export interface GenerateQuestionRequest {
  primary_metric: MetricName;
  use_pool: boolean;
}

export interface SubmitEvaluationRequest {
  response_id: string;
  evaluations: EvaluationsRecord;
}

// API Response Types
export interface GenerateQuestionResponse {
  question_id: string;
  response_id: string;
  question: string;
  model_response: string;
  model_name: string;
  category: string;
  question_type: string | null;
}

export interface SubmitEvaluationResponse {
  evaluation_id: string;
  status: string;
  message: string;
}

export interface AlignmentAnalysis {
  user_score: number | null;
  judge_score: number | null;
  gap: number;
  verdict: 'aligned' | 'over_estimated' | 'under_estimated' | 'significantly_over' | 'significantly_under';
  feedback: string;
}

export interface FeedbackResponse {
  evaluation_id: string;
  status?: 'processing' | 'complete';
  message?: string;
  judge_meta_score?: number;
  overall_feedback?: string;
  alignment_analysis?: Record<MetricName, AlignmentAnalysis>;
  improvement_areas?: string[];
  positive_feedback?: string[];
  past_patterns_referenced?: string[];
}

export interface MetricPerformance {
  avg_gap: number;
  count: number;
  trend: 'improving' | 'stable' | 'declining' | 'insufficient_data';
}

export interface StatsOverviewResponse {
  total_evaluations: number;
  average_meta_score: number;
  metrics_performance: Partial<Record<MetricName, MetricPerformance>>;
  improvement_trend: string;
}

export interface PoolStatsResponse {
  total_questions: number;
  by_metric: Record<string, number>;
  by_category: Record<string, number>;
  by_difficulty: Record<string, number>;
  avg_times_used: number;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  api: string;
  database: string;
  chromadb: string;
}

// UI State Types
export interface EvaluationStep {
  step: 'select_metric' | 'view_question' | 'evaluate' | 'waiting' | 'complete';
  selectedMetric?: MetricName;
  questionData?: GenerateQuestionResponse;
  evaluationId?: string;
}
