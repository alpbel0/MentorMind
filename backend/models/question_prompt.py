"""
Question Prompt ORM Model

SQLAlchemy ORM model for question_prompts table.
Template definitions for question generation.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from backend.models.database import Base

if TYPE_CHECKING:
    from backend.models.question import Question


class QuestionPrompt(Base):
    """
    Question Prompt ORM Model

    Template definitions for Claude-based question generation.
    Each row defines how to generate questions for a specific metric and question type.

    Attributes:
        id: Primary key (auto-increment)
        primary_metric: Main metric being tested (e.g., 'Truthfulness', 'Helpfulness')
        bonus_metrics: Hidden secondary metrics (JSONB array)
        question_type: Type of question (e.g., 'hallucination_test', 'factual_accuracy')
        user_prompt: Prompt template for Claude (contains {category}, {golden_examples} placeholders)
        golden_examples: Example question-answer pairs (JSONB array)
        difficulty: Difficulty level ('easy', 'medium', 'hard')
        category_hints: Category preferences (JSONB array, e.g., ["Math", "Coding"] or ["any"])
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
        questions: Relationship to Question model
    """

    __tablename__ = "question_prompts"

    # =====================================================
    # Primary Key
    # =====================================================

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # =====================================================
    # Core Fields
    # =====================================================

    primary_metric: Mapped[str] = mapped_column(String(50))
    """Main metric being tested. Values: 'Truthfulness', 'Helpfulness', 'Safety', 'Bias', 'Clarity', 'Consistency', 'Efficiency', 'Robustness'"""

    bonus_metrics: Mapped[list[str]] = mapped_column(JSONB, default=list)
    """Array of secondary metric names (JSONB)"""

    question_type: Mapped[str] = mapped_column(String(100))
    """Type of question (e.g., 'hallucination_test', 'factual_accuracy', 'explain_like_5')"""

    user_prompt: Mapped[str] = mapped_column(Text)
    """Prompt template for Claude (contains {category}, {golden_examples} placeholders)"""

    golden_examples: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    """Array of example question-answer pairs (JSONB)"""

    difficulty: Mapped[str] = mapped_column(String(10))
    """Difficulty level: 'easy', 'medium', or 'hard'"""

    category_hints: Mapped[list[str]] = mapped_column(JSONB, default=list)
    """Array of category preferences (JSONB). Either ['any'] alone or non-empty list of categories"""

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

    questions: Mapped[list["Question"]] = relationship(
        back_populates="question_prompt",
        lazy="selectin"
    )
    """List of questions generated from this prompt"""

    # =====================================================
    # Table Constraints
    # =====================================================

    __table_args__ = (
        CheckConstraint("difficulty IN ('easy', 'medium', 'hard')", name="check_difficulty"),
        {"schema": "public"}
    )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"<QuestionPrompt(id={self.id}, primary_metric={self.primary_metric}, "
            f"question_type={self.question_type})>"
        )
