"""
MentorMind - Business Logic Services Package

This package contains service layer for business logic.
"""

# =====================================================
# Claude AI Service
# =====================================================
from backend.services.claude_service import (
    ClaudeService,
    claude_service,
    generate_question,
    select_category,
)

# =====================================================
# Model Service (K Models via OpenRouter)
# =====================================================
from backend.services.model_service import (
    ModelService,
    model_service,
    select_model,
    answer_question,
)

# =====================================================
# LLM Logger Service
# =====================================================
from backend.services.llm_logger import llm_logger, log_llm_call

__all__ = [
    # Claude Service
    "ClaudeService",
    "claude_service",
    "generate_question",
    "select_category",
    # Model Service
    "ModelService",
    "model_service",
    "select_model",
    "answer_question",
    # LLM Logger
    "llm_logger",
    "log_llm_call",
]
