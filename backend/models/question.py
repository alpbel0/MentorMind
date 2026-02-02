"""
Question ORM Model

SQLAlchemy ORM model for questions table.
Generated questions with denormalized metadata.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from backend.models.database import Base

if TYPE_CHECKING:
    from backend.models.question_prompt import QuestionPrompt
    from backend.models.model_response import ModelResponse


class Question(Base):
    """
    Question ORM Model

    Generated questions from Claude with denormalized metadata.
    Each question can be answered by multiple K models.

    Attributes:
        id: Primary key (custom format: q_YYYYMMDD_HHMMSS_randomhex)
        question: Question text
        category: Category (Math, Coding, Medical, General)
        reference_answer: Ideal answer (nullable)
        expected_behavior: What model should do (nullable)
        rubric_breakdown: Score descriptions mapping (JSONB object)
        primary_metric: Denormalized from prompt (main metric being tested)
        bonus_metrics: Denormalized from prompt (JSONB array)
        question_prompt_id: Foreign key to source prompt (nullable)
        times_used: Number of times question has been selected from pool
        first_used_at: Timestamp of first usage (nullable)
        last_used_at: Timestamp of last usage (nullable)
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
        question_prompt: Relationship to QuestionPrompt model
        model_responses: List of responses from K models
    """

    __tablename__ = "questions"

    # =====================================================
    # Primary Key (custom format - service generated)
    # =====================================================

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    """Custom ID format: q_YYYYMMDD_HHMMSS_randomhex"""

    # =====================================================
    # Core Fields
    # =====================================================

    question: Mapped[str] = mapped_column(Text)
    """Question text"""

    category: Mapped[str] = mapped_column(String(50))
    """Category: Math, Coding, Medical, General"""

    difficulty: Mapped[str] = mapped_column(
        Enum("easy", "medium", "hard", name="difficulty_level", create_type=False)
    )
    """Difficulty level ENUM: 'easy', 'medium', or 'hard' (references PostgreSQL ENUM)"""

    reference_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    """Ideal answer (nullable)"""

    expected_behavior: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    """What the model should do (nullable)"""

    rubric_breakdown: Mapped[dict[str, str]] = mapped_column(JSONB)
    """Score descriptions mapping: {'1': 'description', '2': 'description', ...}"""

    # =====================================================
    # Denormalized Fields (from question_prompts)
    # =====================================================

    primary_metric: Mapped[str] = mapped_column(String(50))
    """Main metric being tested (denormalized for query performance)"""

    bonus_metrics: Mapped[list[str]] = mapped_column(JSONB, default=list)
    """Hidden secondary metrics (JSONB array, denormalized for query performance)"""

    question_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    """Question type denormalized from question_prompts (e.g., hallucination_test, factual_accuracy)"""

    # =====================================================
    # Foreign Key
    # =====================================================

    question_prompt_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    """
    Foreign key to source prompt (nullable, set NULL if prompt deleted).
    Note: ForeignKey constraint enforced at database level, not ORM level
    to avoid circular dependency issues.
    """

    # =====================================================
    # Usage Tracking (for pool management)
    # =====================================================

    times_used: Mapped[int] = mapped_column(Integer, default=0)
    """Number of times question has been selected from pool"""

    first_used_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    """Timestamp of first usage (null if never used)"""

    last_used_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    """Timestamp of last usage (null if never used)"""

    # =====================================================
    # Timestamps
    # =====================================================

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    """Timestamp when record was created"""

    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    """Timestamp when record was last updated"""

    # =====================================================
    # Relationships
    # =====================================================

    # Note: Relationships removed to avoid circular dependency issues
    # Use manual joins with FK columns if needed

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"<Question(id={self.id}, category={self.category}, "
            f"difficulty={self.difficulty}, primary_metric={self.primary_metric})>"
        )
