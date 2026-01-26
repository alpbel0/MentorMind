"""
Model Response ORM Model

SQLAlchemy ORM model for model_responses table.
K model answers to questions.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.database import Base

if TYPE_CHECKING:
    from backend.models.question import Question
    from backend.models.user_evaluation import UserEvaluation


# =====================================================
# K Model Names (used in validation)
# =====================================================

K_MODELS = [
    "gpt-3.5-turbo",
    "gpt-4o-mini",
    "claude-3-5-haiku-20241022",
    "gemini-2.0-flash-exp"
]
"""Valid K model names for evaluation"""


class ModelResponse(Base):
    """
    Model Response ORM Model

    Responses from K models (GPT-3.5, GPT-4o-mini, Claude Haiku, Gemini).
    Each model answers each question exactly once.

    Attributes:
        id: Primary key (custom format: resp_YYYYMMDD_HHMMSS_randomhex)
        question_id: Foreign key to questions table
        model_name: Name of the K model that generated the response
        response_text: Model's answer to the question
        evaluated: Whether user has evaluated this response
        created_at: Timestamp when response was created
        question: Relationship to Question model
        user_evaluation: User's evaluation of this response (one-to-one)
    """

    __tablename__ = "model_responses"

    # =====================================================
    # Primary Key (custom format - service generated)
    # =====================================================

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    """Custom ID format: resp_YYYYMMDD_HHMMSS_randomhex"""

    # =====================================================
    # Foreign Key
    # =====================================================

    question_id: Mapped[str] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE")
    )
    """Foreign key to question (deleted if question deleted)"""

    # =====================================================
    # Model Info
    # =====================================================

    model_name: Mapped[str] = mapped_column(String(100))
    """Name of K model that generated response"""

    response_text: Mapped[str] = mapped_column(Text)
    """Model's answer to the question"""

    # =====================================================
    # Evaluation Tracking
    # =====================================================

    evaluated: Mapped[bool] = mapped_column(Boolean, default=False)
    """Whether user has evaluated this response"""

    # =====================================================
    # Timestamps
    # =====================================================

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    """Timestamp when response was created"""

    # =====================================================
    # Relationships
    # =====================================================

    question: Mapped["Question"] = relationship(
        back_populates="model_responses",
        lazy="selectin"
    )
    """Question that this response answers"""

    user_evaluation: Mapped[Optional["UserEvaluation"]] = relationship(
        back_populates="model_response",
        lazy="selectin",
        uselist=False
    )
    """User's evaluation of this response (one-to-one)"""

    # =====================================================
    # Table Constraints
    # =====================================================

    __table_args__ = (
        CheckConstraint(
            f"model_name IN ({','.join(repr(m) for m in K_MODELS)})",
            name="check_model_name"
        ),
        {"schema": "public"}
    )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return f"<ModelResponse(id={self.id}, model_name={self.model_name})>"
