"""
User Evaluation ORM Model

SQLAlchemy ORM model for user_evaluations table.
User's evaluation of model responses.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from backend.models.database import Base

if TYPE_CHECKING:
    from backend.models.model_response import ModelResponse
    from backend.models.judge_evaluation import JudgeEvaluation


class UserEvaluation(Base):
    """
    User Evaluation ORM Model

    User's evaluation of model responses across 8 metrics.
    Judge evaluation runs asynchronously in background.

    Attributes:
        id: Primary key (custom format: eval_YYYYMMDD_HHMMSS_randomhex)
        response_id: Foreign key to model_responses table
        evaluations: Evaluation data (8 metrics with scores and reasoning)
        judged: Whether GPT-4o has evaluated this evaluation
        created_at: Timestamp when evaluation was created
        model_response: Relationship to ModelResponse (one-to-one)
        judge_evaluation: GPT-4o's two-stage evaluation (one-to-one)
    """

    __tablename__ = "user_evaluations"

    # =====================================================
    # Primary Key (custom format - service generated)
    # =====================================================

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    """Custom ID format: eval_YYYYMMDD_HHMMSS_randomhex"""

    # =====================================================
    # Foreign Key (we own this relationship)
    # =====================================================

    response_id: Mapped[str] = mapped_column(
        ForeignKey("model_responses.id", ondelete="CASCADE")
    )
    """Foreign key to model response (deleted if response deleted)"""

    # =====================================================
    # Evaluation Data (8 metrics)
    # =====================================================

    evaluations: Mapped[dict[str, dict]] = mapped_column(JSONB)
    """
    User's evaluation across 8 metrics (JSONB).

    Structure:
    {
        "Truthfulness": {"score": 3, "reasoning": "..."},
        "Helpfulness": {"score": null, "reasoning": "N/A"},
        "Safety": {"score": 5, "reasoning": "..."},
        "Bias": {"score": null, "reasoning": "N/A"},
        "Clarity": {"score": 4, "reasoning": "..."},
        "Consistency": {"score": null, "reasoning": "N/A"},
        "Efficiency": {"score": 5, "reasoning": "..."},
        "Robustness": {"score": 2, "reasoning": "..."}
    }

    Score values: 1-5 (integer) or null (not applicable)
    """

    # =====================================================
    # Judge Tracking
    # =====================================================

    judged: Mapped[bool] = mapped_column(Boolean, default=False)
    """Whether GPT-4o has evaluated this evaluation"""

    # =====================================================
    # Timestamps
    # =====================================================

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    """Timestamp when evaluation was created"""

    # =====================================================
    # Relationships
    # =====================================================

    model_response: Mapped["ModelResponse"] = relationship(
        back_populates="user_evaluation",
        lazy="selectin"
    )
    """Model response that was evaluated (one-to-one, we own FK)"""

    judge_evaluation: Mapped[Optional["JudgeEvaluation"]] = relationship(
        back_populates="user_evaluation",
        lazy="selectin",
        uselist=False
    )
    """GPT-4o's two-stage evaluation (one-to-one, judge owns FK to us)"""

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return f"<UserEvaluation(id={self.id}, judged={self.judged})>"
