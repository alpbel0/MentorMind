"""
Pydantic Schemas for MentorMind

Validation schemas for API requests and responses.
Uses Pydantic v2 syntax.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from backend.constants.metrics import ALL_METRIC_SLUGS, is_valid_slug


# =====================================================
# Constants
# =====================================================

EVALUATION_METRICS = [
    "Truthfulness",
    "Helpfulness",
    "Safety",
    "Bias",
    "Clarity",
    "Consistency",
    "Efficiency",
    "Robustness"
]
"""The 8 evaluation metrics used in MentorMind"""

K_MODELS = [
    "mistralai/mistral-nemo",
    "qwen/qwen-2.5-7b-instruct",
    "deepseek/deepseek-chat",
    "google/gemini-2.0-flash-001",
    "openai/gpt-4o-mini",
    "openai/gpt-3.5-turbo",
]
"""Valid K model names for evaluation (via OpenRouter)"""

DIFFICULTY_LEVELS = ["easy", "medium", "hard"]
"""Valid difficulty levels for questions"""

CATEGORIES = ["Math", "Coding", "Medical", "General"]
"""Valid question categories"""


# =====================================================
# Validators
# =====================================================

def validate_score_range(v: int | None) -> int | None:
    """
    Validate score is 1-5 or None.

    Args:
        v: Score value to validate

    Returns:
        Validated score (1-5 or None)

    Raises:
        ValueError: If score is not None and not between 1 and 5
    """
    if v is not None and not (1 <= v <= 5):
        raise ValueError("Score must be between 1 and 5, or null")
    return v


def validate_metrics_dict(v: dict) -> dict:
    """
    Validate all 8 metrics are present in evaluations.

    Args:
        v: Evaluations dictionary to validate

    Returns:
        Validated evaluations dictionary

    Raises:
        ValueError: If not all 8 metrics are present
    """
    if set(v.keys()) != set(EVALUATION_METRICS):
        raise ValueError(f"Must include all 8 metrics: {EVALUATION_METRICS}")
    return v


def validate_category_hints(v: list[str]) -> list[str]:
    """
    Validate category_hints business rule:
    - Either ["any"] alone
    - OR non-empty list of valid categories (no mixing "any" with others)

    Args:
        v: Category hints list to validate

    Returns:
        Validated category hints list

    Raises:
        ValueError: If validation fails
    """
    if not v:
        raise ValueError("category_hints cannot be empty")
    if "any" in v:
        if len(v) != 1:
            raise ValueError("If 'any' is present, it must be the only element")
    return v


# =====================================================
# QuestionPrompt Schemas
# =====================================================

class QuestionPromptBase(BaseModel):
    """Base fields for QuestionPrompt schemas."""

    primary_metric: str = Field(..., description="Main metric being tested")
    bonus_metrics: list[str] = Field(default_factory=list, description="Hidden secondary metrics")
    question_type: str = Field(..., description="Type of question (e.g., 'hallucination_test')")
    user_prompt: str = Field(..., description="Prompt template for Claude")
    golden_examples: list[dict] = Field(default_factory=list, description="Example Q&A pairs")
    difficulty: str = Field(..., description="Difficulty level")
    category_hints: list[str] = Field(default_factory=lambda: ["any"], description="Category preferences (default: ['any'])")
    is_active: bool = Field(default=True, description="Whether prompt is active")

    _validate_category_hints = field_validator('category_hints')(validate_category_hints)


class QuestionPromptCreate(QuestionPromptBase):
    """Schema for creating a new QuestionPrompt."""

    pass


class QuestionPromptResponse(QuestionPromptBase):
    """Schema for QuestionPrompt response."""

    id: int = Field(..., description="Question prompt ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


# =====================================================
# Question Schemas
# =====================================================

class QuestionBase(BaseModel):
    """Base fields for Question schemas."""

    question: str = Field(..., description="Question text")
    category: str = Field(..., description="Question category")
    difficulty: str = Field(..., description="Difficulty level")
    reference_answer: Optional[str] = Field(None, description="Ideal answer")
    expected_behavior: Optional[str] = Field(None, description="What model should do")
    rubric_breakdown: dict[str, str] = Field(..., description="Score descriptions (1-5)")
    primary_metric: str = Field(..., description="Main metric being tested")
    bonus_metrics: list[str] = Field(default_factory=list, description="Hidden secondary metrics")
    question_type: Optional[str] = Field(None, description="Question type (e.g., hallucination_test)")


class QuestionCreate(QuestionBase):
    """Schema for creating a new Question."""

    id: str = Field(..., description="Question ID (service-generated)")
    question_prompt_id: Optional[int] = Field(None, description="Source prompt ID")


class QuestionResponse(QuestionBase):
    """Schema for Question response."""

    id: str = Field(..., description="Question ID")
    question_prompt_id: Optional[int] = Field(None, description="Source prompt ID")
    times_used: int = Field(default=0, description="Times selected from pool")
    first_used_at: Optional[datetime] = Field(None, description="First usage timestamp")
    last_used_at: Optional[datetime] = Field(None, description="Last usage timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class QuestionPoolStats(BaseModel):
    """Schema for question pool statistics."""

    total_questions: int = Field(..., description="Total questions in pool")
    by_metric: dict[str, int] = Field(default_factory=dict, description="Questions per metric")
    by_category: dict[str, int] = Field(default_factory=dict, description="Questions per category")
    by_difficulty: dict[str, int] = Field(default_factory=dict, description="Questions per difficulty")
    avg_times_used: float = Field(..., description="Average times used")


# =====================================================
# ModelResponse Schemas
# =====================================================

class ModelResponseBase(BaseModel):
    """Base fields for ModelResponse schemas."""

    model_name: str = Field(..., description="Name of K model")
    response_text: str = Field(..., description="Model's answer")


class ModelResponseCreate(ModelResponseBase):
    """Schema for creating a new ModelResponse."""

    id: str = Field(..., description="Response ID (service-generated)")
    question_id: str = Field(..., description="Question ID")


class ModelResponseResponse(ModelResponseBase):
    """Schema for ModelResponse response."""

    id: str = Field(..., description="Response ID")
    question_id: str = Field(..., description="Question ID")
    evaluated: bool = Field(default=False, description="Whether evaluated by user")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


# =====================================================
# UserEvaluation Schemas
# =====================================================

class MetricEvaluation(BaseModel):
    """Single metric evaluation with score and reasoning."""

    score: Optional[int] = Field(None, ge=1, le=5, description="Score (1-5 or null)")
    reasoning: str = Field(..., description="Explanation for score")


class UserEvaluationBase(BaseModel):
    """Base fields for UserEvaluation schemas."""

    evaluations: dict[str, MetricEvaluation] = Field(
        ...,
        description="Evaluation across all 8 metrics"
    )


class UserEvaluationCreate(UserEvaluationBase):
    """Schema for creating a new UserEvaluation."""

    response_id: str = Field(..., description="Model response ID being evaluated")
    id: str = Field(..., description="Evaluation ID (service-generated)")

    _validate_metrics = field_validator('evaluations')(validate_metrics_dict)


class UserEvaluationResponse(UserEvaluationBase):
    """Schema for UserEvaluation response."""

    id: str = Field(..., description="Evaluation ID")
    response_id: str = Field(..., description="Model response ID")
    judged: bool = Field(default=False, description="Whether judged by GPT-4o")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


# =====================================================
# Evaluation Submission Schemas (API Request/Response)
# =====================================================

class EvaluationSubmitRequest(BaseModel):
    """Request schema for evaluation submission."""

    response_id: str = Field(..., description="Model response ID being evaluated")
    evaluations: dict[str, MetricEvaluation] = Field(
        ...,
        description="Evaluation across all 8 metrics"
    )

    _validate_metrics = field_validator('evaluations')(validate_metrics_dict)


class EvaluationSubmitResponse(BaseModel):
    """Response schema for evaluation submission."""

    evaluation_id: str = Field(..., description="Evaluation ID")
    status: str = Field(default="submitted", description="Submission status")
    message: str = Field(
        default="Evaluation submitted successfully",
        description="Status message"
    )


# =====================================================
# JudgeEvaluation Schemas
# =====================================================

class AlignmentMetric(BaseModel):
    """Per-metric alignment analysis."""

    user_score: Optional[int] = Field(None, ge=1, le=5, description="User's score (null if N/A)")
    judge_score: Optional[int] = Field(None, ge=1, le=5, description="Judge's score (null if N/A)")
    gap: int | float = Field(..., description="Score difference")
    verdict: str = Field(..., description="Alignment verdict")
    feedback: str = Field(..., description="Detailed feedback")


class JudgeEvaluationBase(BaseModel):
    """Base fields for JudgeEvaluation schemas."""

    independent_scores: dict[str, dict] = Field(
        ...,
        description="Stage 1: GPT-4o blind evaluation"
    )
    alignment_analysis: dict[str, AlignmentMetric] = Field(
        ...,
        description="Stage 2: Per-metric gap analysis"
    )
    judge_meta_score: int = Field(
        ...,
        ge=1,
        le=5,
        description="Overall evaluation quality (1-5)"
    )
    overall_feedback: str = Field(..., description="Summary feedback")
    improvement_areas: list[str] = Field(default_factory=list, description="Areas to improve")
    positive_feedback: list[str] = Field(default_factory=list, description="What user did well")
    primary_metric: str = Field(..., description="Primary metric being tested")
    primary_metric_gap: float = Field(..., description="User-judge gap for primary metric")
    weighted_gap: float = Field(..., description="Weighted gap (70% primary, 20% bonus, 10% other)")


class JudgeEvaluationCreate(JudgeEvaluationBase):
    """Schema for creating a new JudgeEvaluation."""

    id: str = Field(..., description="Judge evaluation ID (service-generated)")
    user_evaluation_id: str = Field(..., description="User evaluation ID being judged")
    vector_context: Optional[dict] = Field(None, description="Past mistakes from ChromaDB")


class JudgeEvaluationResponse(JudgeEvaluationBase):
    """Schema for JudgeEvaluation response."""

    id: str = Field(..., description="Judge evaluation ID")
    user_evaluation_id: str = Field(..., description="User evaluation ID")
    vector_context: Optional[dict] = Field(None, description="Past mistakes from ChromaDB")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


class JudgeFeedbackResponse(BaseModel):
    """Complete feedback response for API."""

    evaluation_id: str = Field(..., description="Evaluation ID")
    judge_meta_score: int = Field(..., ge=1, le=5, description="Overall evaluation quality")
    overall_feedback: str = Field(..., description="Summary feedback")
    alignment_analysis: dict[str, AlignmentMetric] = Field(..., description="Per-metric analysis")
    improvement_areas: list[str] = Field(default_factory=list, description="Areas to improve")
    positive_feedback: list[str] = Field(default_factory=list, description="What user did well")
    past_patterns_referenced: list[str] = Field(
        default_factory=list,
        description="Past mistake patterns from ChromaDB"
    )


# =====================================================
# Statistics Schemas
# =====================================================

class MetricPerformance(BaseModel):
    """Performance statistics for a single metric."""

    avg_gap: float = Field(..., description="Average user-judge gap")
    count: int = Field(..., description="Number of evaluations")
    trend: str = Field(..., description="Trend: 'improving', 'stable', or 'declining'")


class StatsOverview(BaseModel):
    """Overview of user performance statistics."""

    total_evaluations: int = Field(..., description="Total number of evaluations")
    average_meta_score: float = Field(..., description="Average judge meta score")
    metrics_performance: dict[str, MetricPerformance] = Field(
        default_factory=dict,
        description="Performance per metric"
    )
    improvement_trend: str = Field(..., description="Overall improvement trend")


# =====================================================
# Evidence Schemas (Coach Chat & Evidence)
# =====================================================

class EvidenceItem(BaseModel):
    """Single evidence item with text highlight."""

    start: int = Field(..., ge=0, description="Start character position")
    end: int = Field(..., gt=0, description="End character position")
    quote: str = Field(..., description="Highlighted text excerpt")
    why: str = Field(..., description="Why this is evidence")
    better: Optional[str] = Field(None, description="Better alternative")
    verified: bool = Field(default=False, description="Whether verified by judge")
    highlight_available: bool = Field(default=True, description="Whether UI can highlight")


class MetricEvidence(BaseModel):
    """Evidence for a single metric with score comparison."""

    metric_slug: str = Field(..., description="Metric slug (e.g., 'truthfulness')")
    user_score: Optional[int] = Field(None, ge=1, le=5, description="User's score")
    judge_score: Optional[int] = Field(None, ge=1, le=5, description="Judge's score")
    metric_gap: float = Field(..., description="Score difference")
    user_reason: str = Field(..., description="User's reasoning")
    judge_reason: str = Field(..., description="Judge's rationale")
    evidence: list[EvidenceItem] = Field(default_factory=list, description="Evidence items")


class EvidenceByMetric(BaseModel):
    """All evidence grouped by metric slug."""

    evidence_by_metric: dict[str, list[EvidenceItem]] = Field(
        default_factory=dict,
        description="Evidence items keyed by metric slug"
    )


# =====================================================
# Snapshot Schemas (Coach Chat & Evidence)
# =====================================================

VALID_SNAPSHOT_STATUSES = ["active", "completed", "archived"]
"""Valid snapshot status values"""


class SnapshotBase(BaseModel):
    """Base fields for Snapshot schemas."""

    question: str = Field(..., description="Question text")
    model_answer: str = Field(..., description="Model's response")
    model_name: str = Field(..., description="K model name")
    judge_model: str = Field(default="gpt-4o", description="Judge model")
    primary_metric: str = Field(..., description="Primary metric slug")
    bonus_metrics: list[str] = Field(default_factory=list, description="Bonus metric slugs")
    category: Optional[str] = Field(None, description="Question category")


class SnapshotResponse(SnapshotBase):
    """Full snapshot response with all fields."""

    id: str = Field(..., description="Snapshot ID")
    question_id: str = Field(..., description="Original question ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Scores
    user_scores_json: dict[str, dict] = Field(..., description="User scores by metric slug")
    judge_scores_json: dict[str, dict] = Field(..., description="Judge scores by metric slug")

    # Evidence
    evidence_json: Optional[dict] = Field(None, description="Evidence by metric")

    # Judge summary
    judge_meta_score: int = Field(..., ge=1, le=5, description="Overall evaluation quality")
    weighted_gap: float = Field(..., description="Weighted gap score")
    overall_feedback: Optional[str] = Field(None, description="Judge summary")

    # Source references
    user_evaluation_id: Optional[str] = Field(None, description="User evaluation ID")
    judge_evaluation_id: Optional[str] = Field(None, description="Judge evaluation ID")

    # Chat metadata
    chat_turn_count: int = Field(default=0, description="Number of chat turns")
    max_chat_turns: int = Field(default=15, description="Maximum chat turns")
    status: str = Field(..., description="Snapshot status")
    deleted_at: Optional[datetime] = Field(None, description="Soft delete timestamp")

    # Computed property (added manually when creating response)
    is_chat_available: bool = Field(..., description="Whether chat is available")

    model_config = {"from_attributes": True}


class SnapshotListItem(BaseModel):
    """Single item in snapshot list (minimal fields)."""

    id: str = Field(..., description="Snapshot ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    primary_metric: str = Field(..., description="Primary metric slug")
    category: Optional[str] = Field(None, description="Question category")
    judge_meta_score: int = Field(..., ge=1, le=5, description="Overall evaluation quality")
    status: str = Field(..., description="Snapshot status")
    chat_turn_count: int = Field(default=0, description="Number of chat turns")

    model_config = {"from_attributes": True}


class SnapshotListResponse(BaseModel):
    """Paginated list of snapshots."""

    items: list[SnapshotListItem] = Field(..., description="Snapshot items")
    total: int = Field(..., description="Total number of snapshots")
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, description="Items per page")


# =====================================================
# Chat Schemas (Coach Chat & Evidence)
# =====================================================

VALID_CHAT_ROLES = ["user", "assistant"]
"""Valid chat role values"""


def validate_metric_slugs(v: list[str]) -> list[str]:
    """
    Validate metric slugs list (max 3 items).

    Args:
        v: List of metric slugs to validate

    Returns:
        Validated metric slugs list

    Raises:
        ValueError: If more than 3 items or invalid slug found
    """
    if len(v) > 3:
        raise ValueError("selected_metrics can have at most 3 items")
    for slug in v:
        if not is_valid_slug(slug):
            raise ValueError(
                f"Invalid metric slug: '{slug}'. Valid slugs: {ALL_METRIC_SLUGS}"
            )
    return v


def validate_client_message_id(v: str) -> str:
    """
    Validate client_message_id is a non-empty string.

    Args:
        v: Client message ID to validate

    Returns:
        Validated client message ID

    Raises:
        ValueError: If empty or whitespace only
    """
    if not v or not v.strip():
        raise ValueError("client_message_id cannot be empty")
    return v


def validate_chat_role(v: str) -> str:
    """
    Validate chat role is either 'user' or 'assistant'.

    Args:
        v: Chat role to validate

    Returns:
        Validated chat role

    Raises:
        ValueError: If not a valid role
    """
    if v not in VALID_CHAT_ROLES:
        raise ValueError(f"Invalid role: '{v}'. Valid roles: {VALID_CHAT_ROLES}")
    return v


class ChatMessageBase(BaseModel):
    """Base fields for ChatMessage schemas."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(default="", description="Message content")

    _validate_role = field_validator('role')(validate_chat_role)


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a new chat message."""

    snapshot_id: str = Field(..., description="Snapshot ID")
    client_message_id: str = Field(..., description="Client-generated UUID for idempotency")
    selected_metrics: Optional[list[str]] = Field(None, description="Selected metric slugs (user only)")

    _validate_client_id = field_validator('client_message_id')(validate_client_message_id)
    _validate_metrics = field_validator('selected_metrics')(validate_metric_slugs)


class ChatMessageResponse(ChatMessageBase):
    """Schema for chat message response."""

    id: str = Field(..., description="Message ID")
    snapshot_id: str = Field(..., description="Snapshot ID")
    client_message_id: str = Field(..., description="Shared turn ID")
    is_complete: bool = Field(default=True, description="Whether message is complete")
    selected_metrics: Optional[list[str]] = Field(None, description="Selected metric slugs")
    token_count: int = Field(default=0, description="Token count")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    """Request schema for sending a chat message."""

    message: str = Field(..., min_length=1, description="User message content")
    client_message_id: str = Field(..., description="Client-generated UUID for idempotency")
    selected_metrics: list[str] = Field(
        default_factory=list,
        description="Selected metric slugs (max 3)"
    )
    is_init: bool = Field(default=False, description="Whether this is the first message")

    _validate_client_id = field_validator('client_message_id')(validate_client_message_id)
    _validate_metrics = field_validator('selected_metrics')(validate_metric_slugs)


class ChatHistoryResponse(BaseModel):
    """Response schema for chat history."""

    messages: list[ChatMessageResponse] = Field(..., description="Chat messages")
    total: int = Field(..., description="Total message count")
    snapshot_id: str = Field(..., description="Snapshot ID")
    is_chat_available: bool = Field(..., description="Whether chat is available")
    turns_remaining: int = Field(..., description="Remaining chat turns")
