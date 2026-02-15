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

// ── Metric Slug System (Phase 3) ──

export type MetricSlug =
  | 'truthfulness'
  | 'helpfulness'
  | 'safety'
  | 'bias'
  | 'clarity'
  | 'consistency'
  | 'efficiency'
  | 'robustness';

// ── Evidence Types (Phase 3) ──

export interface EvidenceItem {
  start: number;
  end: number;
  quote: string;
  why: string;
  better: string | null;
  verified: boolean;
  highlight_available: boolean;
}

export interface MetricEvidence {
  user_score: number | null;
  judge_score: number | null;
  metric_gap: number;
  user_reason?: string;
  judge_reason?: string;
  evidence: EvidenceItem[];
}

export type EvidenceByMetric = Record<string, MetricEvidence>;

// ── Snapshot Types (Phase 3) ──

export interface SnapshotListItem {
  id: string;
  created_at: string;
  primary_metric: string;
  category: string;
  judge_meta_score: number;
  status: 'active' | 'completed' | 'archived';
  chat_turn_count: number;
  model_name?: string;
  weighted_gap?: number;
}

export interface SnapshotListResponse {
  items: SnapshotListItem[];
  total: number;
  page: number;
  per_page: number;
}

export interface SnapshotResponse {
  id: string;
  created_at: string;
  updated_at?: string;
  question_id: string;
  question: string;
  model_answer: string;
  model_name: string;
  judge_model: string;
  primary_metric: string;
  bonus_metrics: string[];
  category: string;
  user_scores_json: Record<string, { score: number | null; reasoning: string }>;
  judge_scores_json: Record<string, { score: number | null; rationale?: string; reasoning?: string }>;
  evidence_json: Record<string, EvidenceItem[]> | null;
  judge_meta_score: number;
  weighted_gap: number;
  overall_feedback: string;
  user_evaluation_id: string;
  judge_evaluation_id: string;
  chat_turn_count: number;
  max_chat_turns: number;
  status: 'active' | 'completed' | 'archived';
  deleted_at: string | null;
  is_chat_available: boolean;
}

// ── Chat Types (Phase 3) ──

export interface ChatMessage {
  id: string;
  snapshot_id: string;
  client_message_id: string;
  role: 'user' | 'assistant';
  content: string;
  is_complete: boolean;
  selected_metrics: string[] | null;
  token_count: number;
  created_at: string;
}

export interface ChatHistoryResponse {
  snapshot_id: string;
  messages: ChatMessage[];
  total: number;
  is_chat_available: boolean;
  turns_remaining: number;
}

export interface ChatRequest {
  message: string;
  client_message_id: string;
  selected_metrics: string[];
  is_init: boolean;
}

// UI State Types
export interface EvaluationStep {
  step: 'select_metric' | 'view_question' | 'evaluate' | 'waiting' | 'complete';
  selectedMetric?: MetricName;
  questionData?: GenerateQuestionResponse;
  evaluationId?: string;
}
