"""
EvaluationSnapshot ORM Model

Immutable snapshots of completed evaluations for Coach Chat & Evidence.
Isolated from live tables - source deletions don't affect chat history.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Integer, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, ENUM

from backend.models.database import Base

if TYPE_CHECKING:
    from backend.models.chat_message import ChatMessage


class EvaluationSnapshot(Base):
    """
    EvaluationSnapshot ORM Model

    Immutable snapshot of a completed evaluation, used as the foundation
    for Coach Chat conversations. Contains copies of question, answer,
    scores, and evidence to preserve chat history even if source data is deleted.

    Attributes:
        id: Primary key (custom format: snap_YYYYMMDD_HHMMSS_randomhex)
        created_at: Timestamp when snapshot was created
        updated_at: Timestamp when snapshot was last updated
        question_id: Reference to original question (not FK, allows deletion)
        question: Snapshot of question text
        model_answer: Snapshot of model's response
        model_name: Model that provided the answer
        judge_model: Judge model used (default: gpt-4o)
        primary_metric: Primary metric being evaluated (slug format)
        bonus_metrics: Array of metric slugs for bonus metrics
        category: Question category (Math, Coding, Medical, General, etc.)
        user_scores_json: User scores nested by metric slug
        judge_scores_json: Judge scores nested by metric slug
        evidence_json: Per-metric evidence items for Coach Chat highlighting
        judge_meta_score: Overall quality of user's evaluation (1-5)
        weighted_gap: Weighted gap (70% primary, 20% bonus, 10% other)
        overall_feedback: Summary feedback from judge
        user_evaluation_id: Reference to user_evaluations table (nullable)
        judge_evaluation_id: Reference to judge_evaluations table (nullable)
        chat_turn_count: Number of chat turns in conversation
        max_chat_turns: Maximum allowed chat turns (default: 15)
        status: Snapshot status (active, completed, archived)
        deleted_at: Soft delete timestamp (NULL if not deleted)
    """

    __tablename__ = "evaluation_snapshots"

    # =====================================================
    # Primary Key (custom format - service generated)
    # =====================================================

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    """Custom ID format: snap_YYYYMMDD_HHMMSS_randomhex"""

    # =====================================================
    # Timestamps
    # =====================================================

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    """Timestamp when snapshot was created"""

    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    """Timestamp when snapshot was last updated"""

    # =====================================================
    # Question snapshot (immutable copy)
    # =====================================================

    question_id: Mapped[str] = mapped_column(String(50))
    """
    Reference to original question (not FK - question can be deleted
    without affecting snapshot).
    """

    question: Mapped[str] = mapped_column(Text)
    """Snapshot of question text"""

    model_answer: Mapped[str] = mapped_column(Text)
    """Snapshot of model's response"""

    model_name: Mapped[str] = mapped_column(String(100))
    """Model that provided the answer (e.g., gpt-3.5-turbo, claude-3-5-haiku-20241022)"""

    judge_model: Mapped[str] = mapped_column(String(50), default="gpt-4o")
    """Judge model used for evaluation (default: gpt-4o)"""

    # =====================================================
    # Metric information (using SLUG format per Task 11.1)
    # =====================================================

    primary_metric: Mapped[str] = mapped_column(String(50))
    """
    Primary metric being evaluated (slug format).
    Values: 'truthfulness', 'helpfulness', 'safety', 'bias',
            'clarity', 'consistency', 'efficiency', 'robustness'
    """

    bonus_metrics: Mapped[list[str]] = mapped_column(JSONB, default=list)
    """
    Array of metric slugs for bonus metrics.
    Example: ['clarity', 'helpfulness']
    """

    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    """
    Question category.
    Values: Math, Coding, Medical, General, etc.
    """

    # =====================================================
    # Scores (nested by metric slug per user decision)
    # =====================================================

    user_scores_json: Mapped[dict] = mapped_column(JSONB)
    """
    User scores nested by metric slug.

    Structure:
    {
        "truthfulness": {"score": 4, "reasoning": "Good accuracy"},
        "helpfulness": {"score": 3, "reasoning": "Somewhat helpful"},
        ...
    }
    """

    judge_scores_json: Mapped[dict] = mapped_column(JSONB)
    """
    Judge scores nested by metric slug.

    Structure:
    {
        "truthfulness": {"score": 5, "rationale": "Excellent catch"},
        "helpfulness": {"score": 3, "rationale": "Adequate guidance"},
        ...
    }
    """

    # =====================================================
    # Evidence (for Coach Chat - AD-3, AD-7)
    # =====================================================

    evidence_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    """
    Per-metric evidence items for Coach Chat highlighting.

    Structure:
    {
        "truthfulness": [
            {
                "start": 42,
                "end": 87,
                "quote": "...",
                "why": "Hallucination detected",
                "better": "Correct answer is...",
                "verified": true,
                "highlight_available": true
            }
        ],
        "clarity": [...]
    }
    """

    # =====================================================
    # Judge summary
    # =====================================================

    judge_meta_score: Mapped[int] = mapped_column(Integer)
    """
    Overall quality of user's evaluation (1-5).

    1: Very poor alignment (weighted gap > 2.0)
    2: Poor alignment (weighted gap > 1.5)
    3: Moderate alignment (weighted gap > 1.0)
    4: Good alignment (weighted gap > 0.5)
    5: Excellent alignment (weighted gap <= 0.5)
    """

    weighted_gap: Mapped[float] = mapped_column(Float)
    """
    Weighted gap formula:
    - Primary metric gap: 70% weight
    - Bonus metrics gap (average): 20% weight
    - Other metrics gap (average): 10% weight

    Result: 0-5 scale (lower is better)
    """

    overall_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    """Summary feedback from judge"""

    # =====================================================
    # Source references (not FKs - allow source deletion)
    # =====================================================

    user_evaluation_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    """Reference to user_evaluations table (nullable)"""

    judge_evaluation_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    """Reference to judge_evaluations table (nullable)"""

    # =====================================================
    # Chat metadata (AD-9: Turn Limit)
    # =====================================================

    chat_turn_count: Mapped[int] = mapped_column(Integer, default=0)
    """Number of chat turns in conversation"""

    max_chat_turns: Mapped[int] = mapped_column(Integer, default=15)
    """Maximum allowed chat turns (default: 15)"""

    # =====================================================
    # Status and soft delete
    # =====================================================

    status: Mapped[str] = mapped_column(
        ENUM("active", "completed", "archived", name="snapshot_status", create_type=False)
    )
    """
    Snapshot status for Coach Chat lifecycle:
    - active: Chat available for conversation
    - completed: Chat finished by user
    - archived: Retention policy applied
    """

    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    """
    Soft delete timestamp.
    NULL = not deleted, set = soft deleted
    """

    # =====================================================
    # Properties
    # =====================================================

    @property
    def is_chat_available(self) -> bool:
        """
        Check if chat is available for this snapshot.

        Chat is available when:
        - status == 'active'
        - chat_turn_count < max_chat_turns
        - not soft deleted (deleted_at is NULL)

        Returns:
            bool: True if chat can be started/continued, False otherwise
        """
        return (
            self.status == "active"
            and self.chat_turn_count < self.max_chat_turns
            and self.deleted_at is None
        )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"<EvaluationSnapshot(id={self.id}, primary_metric={self.primary_metric}, "
            f"status={self.status}, chat_turn_count={self.chat_turn_count})>"
        )
