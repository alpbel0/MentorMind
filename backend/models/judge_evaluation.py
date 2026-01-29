"""
Judge Evaluation ORM Model

SQLAlchemy ORM model for judge_evaluations table.
GPT-4o's two-stage evaluation of user assessments.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Integer, Float, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from backend.models.database import Base

if TYPE_CHECKING:
    from backend.models.user_evaluation import UserEvaluation


class JudgeEvaluation(Base):
    """
    Judge Evaluation ORM Model

    GPT-4o's two-stage evaluation of user assessments.
    Stage 1: Independent blind scoring. Stage 2: Mentoring comparison.

    Attributes:
        id: Primary key (custom format: judge_YYYYMMDD_HHMMSS_randomhex)
        user_evaluation_id: Foreign key to user_evaluations table
        independent_scores: Stage 1 blind evaluation (8 metrics with scores and rationale)
        alignment_analysis: Stage 2 gap analysis per metric
        judge_meta_score: Overall quality of user's evaluation (1-5)
        overall_feedback: Summary feedback to user
        improvement_areas: List of areas to improve (JSONB array)
        positive_feedback: List of what user did well (JSONB array)
        vector_context: Past mistakes retrieved from ChromaDB (JSONB, nullable)
        primary_metric: Metric being tested (for statistics)
        primary_metric_gap: User-judge gap for primary metric
        weighted_gap: Weighted gap (70% primary, 20% bonus, 10% other)
        created_at: Timestamp when evaluation was created
        user_evaluation: Relationship to UserEvaluation model
    """

    __tablename__ = "judge_evaluations"

    # =====================================================
    # Primary Key (custom format - service generated)
    # =====================================================

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    """Custom ID format: judge_YYYYMMDD_HHMMSS_randomhex"""

    # =====================================================
    # Foreign Key
    # =====================================================

    user_evaluation_id: Mapped[str] = mapped_column(String(50))
    """
    Foreign key to user evaluation (deleted if user evaluation deleted).
    Note: ForeignKey constraint enforced at database level, not ORM level
    to avoid circular dependency issues.
    """

    # =====================================================
    # Stage 1: Independent Evaluation (GPT-4o blind scoring)
    # =====================================================

    independent_scores: Mapped[dict[str, dict]] = mapped_column(JSONB)
    """
    GPT-4o's blind evaluation (without seeing user scores).

    Structure:
    {
        "Truthfulness": {"score": 3, "rationale": "..."},
        "Helpfulness": {"score": 5, "rationale": "..."},
        ...
    }
    """

    # =====================================================
    # Stage 2: Mentoring Comparison (gap analysis)
    # =====================================================

    alignment_analysis: Mapped[dict[str, dict]] = mapped_column(JSONB)
    """
    Per-metric gap analysis comparing user and judge scores.

    Structure:
    {
        "Truthfulness": {
            "user_score": 3,
            "judge_score": 2,
            "gap": 1,
            "verdict": "over_estimated",
            "feedback": "..."
        },
        ...
    }

    Verdict values: "aligned", "over_estimated", "under_estimated", "significantly_off"
    """

    # =====================================================
    # Meta Evaluation
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

    overall_feedback: Mapped[str] = mapped_column(Text)
    """Summary feedback to user"""

    improvement_areas: Mapped[list[str]] = mapped_column(JSONB, default=list)
    """List of areas where user needs improvement (JSONB array)"""

    positive_feedback: Mapped[list[str]] = mapped_column(JSONB, default=list)
    """List of what user did well (JSONB array)"""

    # =====================================================
    # ChromaDB Context
    # =====================================================

    vector_context: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    """
    Past mistakes retrieved from ChromaDB (nullable).

    Structure (flexible):
    {
        "ids": [["eval_001", "eval_042"]],
        "metadatas": [[...]],
        "documents": [[...]],
        "distances": [[0.12, 0.18]]
    }
    """

    # =====================================================
    # Gap Metrics (for statistics)
    # =====================================================

    primary_metric: Mapped[str] = mapped_column(String(50))
    """Primary metric being tested (for statistics queries)"""

    primary_metric_gap: Mapped[float] = mapped_column(Float)
    """User-judge gap for primary metric (absolute difference)"""

    weighted_gap: Mapped[float] = mapped_column(Float)
    """
    Weighted gap formula:
    - Primary metric gap: 70% weight
    - Bonus metrics gap (average): 20% weight
    - Other metrics gap (average): 10% weight

    Result: 0-5 scale (lower is better)
    """

    # =====================================================
    # Timestamps
    # =====================================================

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    """Timestamp when evaluation was created"""

    # =====================================================
    # Relationships
    # =====================================================

    # Note: Relationships removed to avoid circular dependency issues
    # Use manual joins with FK columns if needed

    # =====================================================
    # Table Constraints
    # =====================================================

    __table_args__ = (
        CheckConstraint("judge_meta_score BETWEEN 1 AND 5", name="check_meta_score"),
        {"schema": "public"}
    )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return f"<JudgeEvaluation(id={self.id}, meta_score={self.judge_meta_score})>"
